import os
import re
import json
import requests
from amadeus import Client, ResponseError
import itertools
import concurrent
from concurrent import futures
from .API_Keys import ApiKeys
import logging
from .llc_airlines import llc_list
from .support_objects import amenities, hotels_parameters_list
import haversine as hs
from backend.raw_backend.control_panel.top_static_score import top_static_score_locations
from backend.raw_backend.control_panel.flight_segments_allowed import direct_flights
from backend.raw_backend.control_panel.flight_offers_params import max_offers_per_destination
from backend.raw_backend.control_panel.flight_weights import weights_for_flight_tickets
from backend.raw_backend.control_panel.weights import min_max_scaling_hb, min_max_scaling_lb
from backend.raw_backend.control_panel.flight_offers_params import baggage_required
from zstandard import ZstdDecompressor
import sqlite3


import pickle
import pandas as pd
from datetime import datetime, timedelta, time
from itertools import combinations
from .support_objects import country_names


from .support_objects import country_names

with open('backend/raw_backend/support/databases/airports.pkl', 'rb') as fp:
    airports = pickle.load(fp)

with open('backend/raw_backend/all_reviews.json', 'rb') as fp:
    all_reviews = json.load(fp)


logger = logging.getLogger('django')


def non_stop_flights(data):
    if not data:
        result = 'false'
    else:
        result = 'true'
    return result


def one_stop(days=0):
    if days <= direct_flights:
        return True
    else:
        return False


def time_object(date, date_format='%Y-%m-%d'):
    return datetime.strptime(date, date_format)


def insert_distances(data, origin_coor, list_of_airports):
    data['airport coor'] = data['airport coor'].apply(tuple)
    data_filter = data[data['airport'].isin(list_of_airports)]
    data_filter.insert(2, 'distance from origin',
                       flatten_extend(hs.haversine_vector(list(data_filter.iloc[:, 3]), origin_coor, comb=True)))
    return data_filter


def insert_distances_ski(data, origin_coor, list_of_airports):
    data['Resort coordinates'] = data['Resort coordinates'].apply(tuple)
    data_filter = data[data['airport'].isin(list_of_airports)]
    data_filter.insert(2, 'distance from origin',
                       flatten_extend(hs.haversine_vector(list(data_filter.iloc[:, 3]), origin_coor, comb=True)))
    return data_filter


def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def amadeus_direct_get(departure_location, departure_date, trip_duration,
                       number_of_passingers):  # ova funkcija ima smisla ako amadeus podrzava origin (za jako mali broj gradova ovaj API daje rezultate)
    amadeus = Client(
        client_id=ApiKeys.amadeus_api_key,
        client_secret=ApiKeys.amadeus_api_secret,
        hostname='production'
    )
    try:
        response = amadeus.shopping.flight_destinations.get(
            origin=departure_location,
            departureDate=departure_date,
            duration=trip_duration
        )
        x = response.data
    except ResponseError:
        x = 'service not available for picked origin'
    amadeus_destinations = {}
    for i in x:
        try:
            amadeus_destinations.update({i['destination']: float(i['price']['total']) * number_of_passingers})
        except:
            pass

    return amadeus_destinations


def common_elements(a, b):
    a_set = set(a)
    b_set = set(b)
    # Using filter false
    not_in_a = set(itertools.filterfalse(lambda x: x in a_set, b_set))
    not_in_b = set(itertools.filterfalse(lambda x: x in b_set, a_set))

    result = set(a_set).intersection(set(b_set) - not_in_a).union(set(b_set).intersection(set(a_set) - not_in_b))
    return list(result)


def connected_destinations(departure_location, departure_date,
                           return_date, one_stop_allowed=True,
                           exclude_llc=True):  # ova funkcija trazi destinacije na za koje postoje direktni letovi za izabrane datume
    def call_API_destinations(body):
        response = requests.get(body)
        return response.json()

    list_bodies = [
        f'https://aviation-edge.com/v2/public/flightsFuture?iataCode={departure_location}&type=departure&date={departure_date}&key={ApiKeys.aviation_edge_key}',
        f'https://aviation-edge.com/v2/public/flightsFuture?iataCode={departure_location}&type=arrival&date={return_date}&key={ApiKeys.aviation_edge_key}'
    ]
    num_treads = len(list_bodies)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_treads) as executor:
        for i in executor.map(call_API_destinations, list_bodies):
            results.append(i)

    if exclude_llc == True:  # ovaj blok smo dodali zato sto zelimo da iskljucimo letove sa lowcosterima (amadeus nam ih  ne daje sem u enterprise paketu)
        excluded_departure = filter(lambda item: item['airline']['name'] not in llc_list, results[0])
        excluded_arrival = filter(lambda item: item['airline']['name'] not in llc_list, results[1])
        results = [excluded_departure, excluded_arrival]
    else:
        pass

    departures = []
    arrivals = []
    try:
        for i in results[0]:
            departures.append(i['arrival']['iataCode'].upper())
        for i in results[1]:
            arrivals.append(i['departure']['iataCode'].upper())
    except:
        pass
    try:
        if one_stop_allowed:
            common_element = common_elements(departures, arrivals)
        else:
            common_element = departures + arrivals

    except:
        common_element = 'Nema povezanih letova za izabrane datume'
    return common_element


def all_destinations(destinations):
    all_destinations = []
    # if destinations['amadeus_direct'] != {}:                   #Ovo sluzi za destinacije za koje ima amadeus info (mali broj destinacija)
    #     for key in destinations['amadeus_direct'].keys():
    #         all_destinations.append(key)
    for i in destinations['flight_edge']:
        all_destinations.append(i)

    all_destinations = set(all_destinations)
    return all_destinations


def autocomplete(string='auto'):
    all_found = []
    for airport in airports.keys():
        if string.lower() in (airports[airport]['iata'].lower()
                              and airport.lower()
                              and airports[airport]['name'].lower()
                              and airports[airport]['city'].lower()) \
                or string.lower() == airport.lower():
            all_found.append((airports[airport]['iata'].upper(), airports[airport]['name'].title(),
                              airports[airport]['city'].title()))
    return all_found


def get_top_static(data, adults, children, dep_date, ret_date):
    top_static_country = []
    top_static_cities = []
    top_static_info = []
    top_static_airports = []

    for index, row in data.iterrows():

        if len(top_static_country) < top_static_score_locations:
            top_static_country.append(row.iloc[10])
            top_static_cities.append(row.iloc[6])
            top_static_airports.append(row.iloc[4])
            top_static_info.append({row['index']: {'origin airport': row['origin airport'],
                                                   'destination airport': row['airport'],
                                                   'city': row['city'],
                                                   'adults': adults,
                                                   'children': children,
                                                   'departure date': dep_date,
                                                   'return date': ret_date,
                                                   'country': row['city country'],
                                                   'a_coor': row['airport coor'],
                                                   'cc_coor': row['city coor']
                                                   }})

    # r = min(top_static_score_locations,len(data.loc[:,'city'].unique())) / len(top_static_country)
    #
    # if r > 1:
    #     for i in top_static_country:
    #
    #         t = data[(data['city country'] == i)&(data['city'].isin(top_static_cities) == False)] #&data['airport'].isin(top_static_airports)==False]
    #
    #         if len(top_static_country) == 1:
    #
    #             for j in range(min(math.ceil(r), (len(t) - 1))):
    #                 #t = data[(data['city country'] == i) & (data['city'].isin(top_static_cities) == False) & (data['airport'].isin(top_static_airports)==False)]
    #                 try:
    #                     top_static_info.append({t.iloc[0, 3]: {'origin airport': t.iloc[0, 1],
    #                                                            'destination airport': t.iloc[0, 4],
    #                                                            'city': t.iloc[0, 6],
    #                                                            'adults': adults,
    #                                                            'children': children,
    #                                                            'departure date': dep_date,
    #                                                            'return date': ret_date,
    #                                                            'country': t.iloc[0,10],
    #                                                            'a_coor': t.iloc[0, 7],
    #                                                            'cc_coor': t.iloc[0, 8]}})
    #                     top_static_cities.append(t.iloc[0, 6])
    #                 except:
    #                     pass
    #
    #         else:
    #             for j in range(min(math.floor(r), (len(t) - 1))):
    #                 #t = data[(data['city country'] == i) & (data['city'].isin(top_static_cities) == False) & (data['airport'].isin(top_static_airports)==False)]
    #                 try:
    #                     top_static_info.append({t.iloc[j, 3]: {'origin airport': t.iloc[0, 1],
    #                                                            'destination airport': t.iloc[0, 4],
    #                                                            'city': t.iloc[0, 6],
    #                                                            'adults': adults,
    #                                                            'children': children,
    #                                                            'departure date': dep_date,
    #                                                            'return date': ret_date,
    #                                                            'country': t.iloc[0,10],
    #                                                            'a_coor': t.iloc[0, 7],
    #                                                            'cc_coor': t.iloc[0, 8]}})
    #                     top_static_cities.append(t.iloc[0, 6])
    #                 except:
    #                     pass
    #
    #         top_static_info = top_static_info[:min(len(top_static_info), top_static_score_locations)]

    return top_static_info


def flights_offers(list_of_destinations, origin, return_date, departure, adults, children, non_stop=False):
    def get_flight_offer_amadeus(destination):

        amadeus = Client(
            client_id=ApiKeys.amadeus_api_key,
            client_secret=ApiKeys.amadeus_api_secret,
            hostname='production'
        )

        try:

            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure,
                returnDate=return_date,
                adults=adults,
                children=children,
                nonStop=non_stop_flights(non_stop),
                max=max_offers_per_destination
            )

            return response.data

        except ResponseError as error:
            raise error

    list = list_of_destinations
    results = []
    num_treads = len(list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_treads) as executor:
        for i in executor.map(get_flight_offer_amadeus, list):
            results.append(i)

    # odavde pocinje zezanje

    have_flight = []
    for i in range(len(results)):
        try:
            have_flight.append(results[i][0]['itineraries'][0]['segments'][-1]['arrival']['iataCode'])
        except:
            pass

    return results, have_flight


def compute_difference(nested_list1, nested_list2):
    set2 = set(nested_list2)
    remaining_elements = [element for element in nested_list1 if element not in set2]
    return remaining_elements


def get_segments(flights, destination, ticket):
    to_destination = [flights[destination][ticket]['itineraries'][0]['segments'][0]['departure']['iataCode']]
    for segment in range(len(flights[destination][ticket]['itineraries'][0]['segments'])):
        to_destination.append(
            flights[destination][ticket]['itineraries'][0]['segments'][segment]['arrival']['iataCode'])

    to_origin = []
    for segment in range(len(flights[destination][ticket]['itineraries'][1]['segments'])):
        to_origin.append(flights[destination][ticket]['itineraries'][1]['segments'][segment]['departure']['iataCode'])
    to_origin.append(flights[destination][ticket]['itineraries'][1]['segments'][-1]['arrival']['iataCode'])

    return to_destination, to_origin


def time_difference_in_minutes(arrival_time, going_home_time):
    # Define the timestamps
    start_time = datetime.fromisoformat(arrival_time)
    end_time = datetime.fromisoformat(going_home_time)

    # Calculate the time difference
    time_difference = end_time - start_time

    # Convert time difference to minutes
    minutes_difference = time_difference.total_seconds() / 60

    return minutes_difference


def duration_to_minutes(duration_str):
    # Use regular expression to extract hours and minutes
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)

    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        total_minutes = hours * 60 + minutes
        return total_minutes
    else:
        return None


def generate_traveler_dicts(num_adults, num_children):
    traveler_dicts = []

    for i in range(1, num_adults + 1):
        traveler_dict = {
            "id": str(i),
            "travelerType": "ADULT",
            "fareOptions": [
                "STANDARD"
            ]
        }
        traveler_dicts.append(traveler_dict)

    for i in range(num_adults + 1, num_adults + num_children + 1):
        traveler_dict = {
            "id": str(i),
            "travelerType": "CHILD",
            "fareOptions": [
                "STANDARD"
            ]
        }
        traveler_dicts.append(traveler_dict)

    return traveler_dicts


def amadeus_post(origin,
                 destination,
                 departure_date,
                 return_date,
                 add_one_way_offers,
                 adults,
                 children,
                 max_number_of_connections,
                 checked_bags_only):
    amadeus = Client(
        client_id=ApiKeys.amadeus_api_key,
        client_secret=ApiKeys.amadeus_api_secret,
        hostname='production'
    )

    data = {
        "originDestinations": [
            {
                "id": "1",
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDateTimeRange": {
                    "date": departure_date
                }
            },
            {
                "id": "2",
                "originLocationCode": destination,
                "destinationLocationCode": origin,
                "arrivalDateTimeRange": {
                    "date": return_date

                }
            }
        ],
        "searchCriteria": {
            "maxFlightOffers": 250,
            "allowAlternativeFareOptions": "true",
            "addOneWayOffers": add_one_way_offers,
            "pricingOptions": {"includedCheckedBagsOnly": checked_bags_only},
            "flightFilters": {"connectionRestriction": {"maxNumberOfConnections": max_number_of_connections},
                              "cabinRestriction": {"coverage": "ALL_SEGMENTS"},
                              "additionalInformation": {"chargeableCheckedBags": "true",
                                                        "brandedFares": "true"}
                              }
        },
        "travelers": generate_traveler_dicts(num_adults=adults, num_children=children),

        "sources": [
            "GDS"
        ],

    }

    json_string = json.dumps(data, indent=4)

    body = json.loads(json_string)
    try:
        response = amadeus.shopping.flight_offers_search.post(body)

    except ResponseError as error:
        raise error

    return response.data


# Ovdje treba izbaciti u control panel timedelta
def return_tickets(tickets, departure_date, return_date):
    result = [i for i in tickets if i['oneWay'] == False and datetime.fromisoformat(
        i['itineraries'][0]['segments'][0]['departure']['at']) > datetime.fromisoformat(departure_date) + timedelta(
        days=0, hours=5, minutes=0, seconds=0) and datetime.fromisoformat(
        i['itineraries'][-1]['segments'][-1]['arrival']['at']) < datetime.fromisoformat(return_date) + timedelta(days=1,
                                                                                                                 hours=3,
                                                                                                                 minutes=0,
                                                                                                                 seconds=0)]
    return result


# Ovdje treba izbaciti u control panel timedelta
def one_way_to_dest(tickets, origin, departure_date):
    result = [i for i in tickets if i['oneWay'] == True and i['itineraries'][0]['segments'][0]['departure'][
        'iataCode'] == origin and datetime.fromisoformat(
        i['itineraries'][0]['segments'][0]['departure']['at']) > datetime.fromisoformat(departure_date) + timedelta(
        days=0, hours=5, minutes=0, seconds=0)]
    return result


def one_way_to_origin(tickets, destination, return_date):
    result = [i for i in tickets if i['oneWay'] == True and i['itineraries'][0]['segments'][0]['departure'][
        'iataCode'] == destination and datetime.fromisoformat(
        i['itineraries'][0]['segments'][-1]['arrival']['at']) < datetime.fromisoformat(return_date) + timedelta(days=1,
                                                                                                                hours=3,
                                                                                                                minutes=0,
                                                                                                                seconds=0)]
    return result


def is_baggage_required(trip_duration):
    if trip_duration < baggage_required:
        checked_bags_only = 'false'
    else:
        checked_bags_only = 'true'
    return checked_bags_only


def is_baggage(tickets):
    try:
        x = tickets['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']
        if ('quantity' in x and x['quantity'] > 0) or ('weight' in x and x['weight'] > 15):
            result = True
        else:
            result = False
    except:
        result = False

    # result = [True if ('quantity' in x and x['quantity']>0) or ('weight' in x and x['weight']>15) else False for x in [i['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags'] for i in tickets] ]

    return result


def return_df(tickets, origin, destination, departure_date, return_date):
    tickets = return_tickets(tickets, departure_date=departure_date, return_date=return_date)

    all_params = []
    all_params.append(list(map(lambda x: x['id'], tickets)))
    all_params.append(list(map(lambda x: float(x['price']['grandTotal']), tickets)))
    all_params.append(list(
        map(lambda x: time_difference_in_minutes(arrival_time=x['itineraries'][0]['segments'][-1]['arrival']['at'],
                                                 going_home_time=x['itineraries'][-1]['segments'][0]['departure'][
                                                     'at']), tickets)))
    all_params.append(list(map(lambda x: duration_to_minutes(x['itineraries'][0]['duration']) + duration_to_minutes(
        x['itineraries'][-1]['duration']), tickets)))
    all_params.append(list(map(lambda x: is_baggage(x), tickets)))
    all_params.append(
        list(map(lambda x: len(x['itineraries'][0]['segments']) + len(x['itineraries'][-1]['segments']), tickets)))
    all_params.append(list(
        map(lambda x: datetime.fromisoformat(x['itineraries'][0]['segments'][0]['departure']['at']).strftime('%H:%M'),
            tickets)))
    all_params.append(list(
        map(lambda x: datetime.fromisoformat(x['itineraries'][-1]['segments'][-1]['arrival']['at']).strftime('%H:%M'),
            tickets)))
    return pd.DataFrame(all_params, index=['id', 'price', 'stay on location', 'total flight duration', 'baggage',
                                           'number of segments', 'departure time', 'arrival time']).T


def combo_df(tickets, origin, destination, departure_date, return_date):
    to_dest = one_way_to_dest(tickets=tickets, origin=origin, departure_date=departure_date)
    to_origin = one_way_to_origin(tickets=tickets, destination=destination, return_date=return_date)

    all_params = []
    combinations = list(itertools.product(to_dest, to_origin))
    all_params.append(list(map(lambda x: (x[0]['id'], x[1]['id']), combinations)))
    all_params.append(
        list(map(lambda x: (float(x[0]['price']['grandTotal']) + float(x[1]['price']['grandTotal'])), combinations)))
    all_params.append(list(
        map(lambda x: time_difference_in_minutes(arrival_time=x[0]['itineraries'][0]['segments'][-1]['arrival']['at'],
                                                 going_home_time=x[1]['itineraries'][0]['segments'][0]['departure'][
                                                     'at']), combinations)))
    all_params.append(list(map(lambda x: duration_to_minutes(x[0]['itineraries'][0]['duration']) + duration_to_minutes(
        x[1]['itineraries'][0]['duration']), combinations)))
    all_params.append(list(map(lambda x: all((is_baggage(x[0]), is_baggage(x[1]))), combinations)))
    all_params.append(list(
        map(lambda x: len(x[0]['itineraries'][0]['segments']) + len(x[1]['itineraries'][0]['segments']), combinations)))
    all_params.append(list(
        map(lambda x: datetime.fromisoformat(x[0]['itineraries'][0]['segments'][0]['departure']['at']).strftime(
            '%H:%M'), combinations)))
    all_params.append(list(
        map(lambda x: datetime.fromisoformat(x[1]['itineraries'][0]['segments'][-1]['arrival']['at']).strftime('%H:%M'),
            combinations)))
    return pd.DataFrame(all_params, index=['id', 'price', 'stay on location', 'total flight duration', 'baggage',
                                           'number of segments', 'departure time', 'arrival time']).T


def tickets_weights(final_tickets, activity_tag):
    weights = weights_for_flight_tickets(activity_tag=activity_tag, trip_duration=5)

    scored_tickets = pd.DataFrame()
    scored_tickets['id'] = final_tickets['id']
    scored_tickets['departure time'] = final_tickets['departure time']
    scored_tickets['arrival time'] = final_tickets['arrival time']

    if (final_tickets['price'] == final_tickets['price'].iloc[0]).all():
        scored_tickets['price score'] = 0
    else:
        scored_tickets['price score'] = min_max_scaling_lb(final_tickets['price'])

    if (final_tickets['stay on location'] == final_tickets['stay on location'].iloc[0]).all():
        scored_tickets['stay on location score'] = 0
    else:
        scored_tickets['stay on location score'] = min_max_scaling_hb(final_tickets['stay on location'])
    if (final_tickets['total flight duration'] == final_tickets['total flight duration'].iloc[0]).all():
        scored_tickets['total flight duration score'] = 0
    else:
        scored_tickets['total flight duration score'] = min_max_scaling_lb(final_tickets['total flight duration'])

    if (final_tickets['number of segments'] == final_tickets['number of segments'].iloc[0]).all():
        scored_tickets['number of segments score'] = 0
    else:
        scored_tickets['number of segments score'] = min_max_scaling_lb(final_tickets['number of segments'])
    # ukupni score
    scored_tickets['total score'] = weights['price score'] * scored_tickets['price score'] + weights[
        'stay on location score'] * scored_tickets['stay on location score'] + weights['total flight duration score'] * \
                                    scored_tickets['total flight duration score'] + weights[
                                        'number of segments score'] * scored_tickets['number of segments score']

    return scored_tickets


def get_optimal_ticket(origin='BEG',
                       destination='LHR',
                       children=1,
                       adults=1,
                       departure_date='2024-06-20',
                       return_date='2024-06-29',
                       activity_tag='None',
                       ):
    trip_duration = time_object(return_date).day - time_object(departure_date).day
    checked_bags_only = is_baggage_required(trip_duration=trip_duration)

    #  Pozivamo amadeus post request sa parametrima koje imamo sa frontenda
    tickets = amadeus_post(origin=origin, destination=destination, adults=adults, children=children,
                           max_number_of_connections=1, checked_bags_only=checked_bags_only, add_one_way_offers='true',
                           departure_date=departure_date, return_date=return_date)
    #  Pravimo dataframe za kombinovane karte
    combos = combo_df(tickets=tickets, origin=origin, destination=destination, departure_date=departure_date,
                      return_date=return_date)
    #  Pravimo dataset za povratne karte
    return_tickets = return_df(tickets=tickets, origin=origin, destination=destination, departure_date=departure_date,
                               return_date=return_date)
    #  Spajamo sve karte
    final_tickets = pd.concat([combos, return_tickets], ignore_index=True)
    result = tickets_weights(final_tickets=final_tickets, activity_tag=activity_tag)
    return result, tickets


def get_all_tickets(list_of_destinations, origin, return_date, departure_date, adults, children, activity_tag):
    def get_optimal_ticket(destination ):
        trip_duration = time_object(return_date).day - time_object(departure_date).day
        checked_bags_only = is_baggage_required(trip_duration=trip_duration)

        #  Pozivamo amadeus post request sa parametrima koje imamo sa frontenda
        tickets = amadeus_post(origin=origin, destination=destination, adults=adults, children=children,
                               max_number_of_connections=2, checked_bags_only=checked_bags_only,
                               add_one_way_offers='true',
                               departure_date=departure_date, return_date=return_date)
        #  Pravimo dataframe za kombinovane karte
        combos = combo_df(tickets=tickets, origin=origin, destination=destination, departure_date=departure_date,
                          return_date=return_date)
        #  Pravimo dataset za povratne karte
        return_tickets = return_df(tickets=tickets, origin=origin, destination=destination,
                                   departure_date=departure_date,
                                   return_date=return_date)
        #  Spajamo sve karte
        final_tickets = pd.concat([combos, return_tickets], ignore_index=True)
        result = tickets_weights(final_tickets=final_tickets, activity_tag=activity_tag)

        return result.to_json(), tickets


    list = list_of_destinations
    results = []
    num_treads = len(list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_treads) as executor:
        for i in executor.map(get_optimal_ticket, list):
            results.append(i)

    return results



def pack_data_objects_into_json(data1, data2, data3):
    # List of data objects you want to combine
    data_objects = [data1, data2, data3]

    combined_data = {}

    for offer_id, data_object in enumerate(data_objects, start=1):
        # Tagging each offer's data with an offerId
        combined_data[f"offerId_{offer_id}"] = data_object

    return combined_data



def get_country_codes(country_names_list):
    # Create a reverse dictionary mapping country names to country codes
    country_codes = {v: k for k, v in country_names.items()}

    # Initialize an empty list to store country codes
    country_codes_list = []

    # Iterate over the input list of country names
    for country_name in country_names_list:
        # Get the corresponding country code from the reverse dictionary
        country_code = country_codes.get(country_name)

        # If country code is found, append it to the list
        if country_code:
            country_codes_list.append(country_code)

    return country_codes_list



def get_all_hotels(checkin, checkout, adults, children, list_of_coordinates, radius,
                       currency='EUR', language='en'):
    def get_hotels(coordinates):
        coordinates = eval(coordinates)
        latitude = coordinates[0]
        longitude = coordinates[1]


        url = "https://api.worldota.net/api/b2b/v3/search/serp/geo/"

        payload = json.dumps({
            "checkin": checkin,
            "checkout": checkout,
            "language": language,
            "guests": [
                {
                    "adults": adults,
                    "children": [children]
                }
            ],
            "longitude": longitude,
            "latitude": latitude,
            "radius": radius,  # in meters from center of the city
            "currency": currency
        })
        headers = {
            'Content-Type': 'application/json'
        }
        auth = (ApiKeys.rh_secret, ApiKeys.rh_key)

        response = requests.request("POST", url, headers=headers, data=payload, auth=auth)

        return response.json()

    iterable_list = list_of_coordinates

    results = []
    num_treads = len(iterable_list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_treads) as executor:
        for i in executor.map(get_hotels, iterable_list):
            results.append(i)

    return results


####################### kreiranje databaze hotela i dekompresija zstd file-a


def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('hotels_1.db')
    c = conn.cursor()

    # Create a table to store hotel data
    c.execute('''CREATE TABLE IF NOT EXISTS hotels
                 (id TEXT PRIMARY KEY, data TEXT)''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


def parse_dump(filename: str) -> None:
    """
    The sample of function that can parse a big zstd dump.
    :param filename: path to a zstd archive
    """
    create_database()  # Create the database if it doesn't exist

    with open(filename, "rb") as fh:
        # make decompressor
        dctx = ZstdDecompressor()
        with dctx.stream_reader(fh) as reader:
            conn = sqlite3.connect('hotels_1.db')
            c = conn.cursor()

            previous_line = ""
            while True:
                # we will read the file by 16mb chunk
                chunk = reader.read(2 ** 24)
                if not chunk:
                    break

                raw_data = previous_line + chunk.decode("utf-8", errors='ignore')
                # all JSON files split by the new line char "\n"
                # try to read one by one
                lines = raw_data.split("\n")
                for line in lines[:-1]:
                    if line:
                        try:
                            hotel_data = json.loads(line)
                            # Insert hotel data into the database
                            c.execute("INSERT OR REPLACE INTO hotels (id, data) VALUES (?, ?)",
                                      (hotel_data['id'], json.dumps(hotel_data)))
                        except json.JSONDecodeError:
                            pass  # skip lines that can't be parsed

                previous_line = lines[-1]

            # Handle the last line if it's a complete JSON
            try:
                hotel_data = json.loads(previous_line)
                c.execute("INSERT OR REPLACE INTO hotels (id, data) VALUES (?, ?)",
                          (hotel_data['id'], json.dumps(hotel_data)))
            except json.JSONDecodeError:
                pass  # skip the last line if it can't be parsed

            # Commit changes and close connection
            conn.commit()
            conn.close()


def find_hotel_by_id(hotel_id: str) -> dict:
    conn = sqlite3.connect('hotels.db')
    c = conn.cursor()

    c.execute("SELECT data FROM hotels WHERE id=?", (hotel_id,))
    result = c.fetchone()

    conn.close()

    if result:
        if type(result[0]) != dict and result[0].endswith('_modified'):
            json_string = result[0]
            cleaned_json_string = json_string[:-9]
            cleaned_json_string = json.loads(cleaned_json_string)
        else:
            cleaned_json_string = json.loads(result[0])
        if type(cleaned_json_string) != dict:
            cleaned_json_string = json.loads(cleaned_json_string)
        else:
            cleaned_json_string = cleaned_json_string

        return cleaned_json_string  # Hotel not found


def find_hotels_by_ids(hotel_ids):
    # Initialize the result dictionary
    result = {}

    # Iterate over each hotel_id in the list and populate the dictionary
    for hotel_id in hotel_ids:
        result[hotel_id] = find_hotel_by_id(hotel_id)

    return result


def get_hotel_amenities(hotel, amenity_list=amenities, reviews=all_reviews):
    # Function to process hotel data and return a dictionary
    kind = hotel.get('kind')
    latitude = hotel.get('latitude')
    longitude = hotel.get('longitude')
    no_of_images = len(hotel.get('images', []))
    try:
        rooms_number = hotel.get('facts', {}).get('rooms_number')
    except:
        rooms_number = None
    star_rating = hotel.get('star_rating')
    check_in = hotel.get('check_in_time')
    check_out = hotel.get('check_out_time')

    try:  # reviews[hotel['id']]:
        total_rating = reviews[hotel['id']]['rating']

        if reviews[hotel['id']]['detailed_ratings']['cleanness']:
            cleanness_rating = reviews[hotel['id']]['detailed_ratings']['cleanness']
        else:
            cleanness_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['location']:
            location_rating = reviews[hotel['id']]['detailed_ratings']['location']
        else:
            location_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['price']:
            price_rating = reviews[hotel['id']]['detailed_ratings']['price']
        else:
            price_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['services']:
            services_rating = reviews[hotel['id']]['detailed_ratings']['services']
        else:
            services_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['room']:
            room_rating = reviews[hotel['id']]['detailed_ratings']['room']
        else:
            room_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['meal']:
            meal_rating = reviews[hotel['id']]['detailed_ratings']['meal']
        else:
            meal_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['wifi']:
            wifi_rating = reviews[hotel['id']]['detailed_ratings']['wifi']
        else:
            wifi_rating = total_rating

        if reviews[hotel['id']]['detailed_ratings']['hygiene']:
            hygiene_rating = reviews[hotel['id']]['detailed_ratings']['hygiene']
        else:
            hygiene_rating = total_rating

    except:
        total_rating = cleanness_rating = room_rating = services_rating = meal_rating = hygiene_rating = wifi_rating = price_rating = location_rating = None
        reviews[hotel['id']] = {'total_rating': total_rating,
                                'detailed_ratings': {'cleanness_rating': cleanness_rating,
                                                     'room_rating': room_rating,
                                                     'services_rating': services_rating,
                                                     'meal_rating': meal_rating,
                                                     'hygiene_rating': hygiene_rating,
                                                     'wifi_rating': wifi_rating,
                                                     'price_rating': price_rating,
                                                     'location_rating': location_rating, }}

    vector = {
        'kind': kind,
        'star_rating': star_rating,
        'rooms_number': rooms_number,
        'latitude': latitude,
        'longitude': longitude,
        'no_of_images': no_of_images,
        'total_rating': total_rating,
        'cleanness_rating': cleanness_rating,
        'room_rating': room_rating,
        'services_rating': services_rating,
        'meal_rating': meal_rating,
        'hygiene_rating': hygiene_rating,
        'wifi_rating': wifi_rating,
        'price_rating': price_rating,
        'location_rating': location_rating,
        'check_in': check_in,
        'check_out': check_out
    }

    copy = amenity_list.copy()
    if hotel.get('amenity_groups'):
        for group in hotel['amenity_groups']:
            hotel_amenities = {amenity: 1 for amenity in group['amenities']}
            copy.update(hotel_amenities)

    vector.update(copy)
    return vector  # Return as dictionary with hotel_id as key


def insert_record(x):
    # Connect to SQLite database (create if not exists)
    conn = sqlite3.connect('records.db')
    cursor = conn.cursor()

    try:
        # Calculate f(x)
        try:
            fx_dict = get_hotel_amenities(find_hotel_by_id(x))
        except:
            fx_dict = json.dumps(get_hotel_amenities(find_hotel_by_id(x)))

        # Convert fx_dict to JSON string
        fx_json = json.dumps(fx_dict)

        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                x TEXT PRIMARY KEY,
                fx TEXT
            )
        ''')

        # Insert record into the database
        cursor.execute('INSERT INTO records (x, fx) VALUES (?, ?)', (x, fx_json))
        conn.commit()



    except sqlite3.Error as e:
        # print(f"Error inserting record: {e}")
        pass
    finally:
        # Close connection
        conn.close()


def fetch_record(primary_key):
    # Connect to SQLite database
    conn = sqlite3.connect('records.db')
    cursor = conn.cursor()

    try:
        # Execute SELECT query
        cursor.execute('SELECT fx FROM records WHERE x = ?', (primary_key,))
        result = cursor.fetchone()

        if result:
            # 'fx' is in the first element of the tuple
            fx_json = result[0]
            fx_dict = json.loads(fx_json)  # Convert JSON string back to dictionary
            return fx_dict
        else:
            print(f"No record found for primary key '{primary_key}'")

    except sqlite3.Error as e:
        print(f"Error fetching record: {e}")

    finally:
        # Close connection
        conn.close()


import sqlite3
import json

import sqlite3
import json


def fetch_records(primary_keys):
    # Connect to SQLite database
    conn = sqlite3.connect('records.db')
    cursor = conn.cursor()

    results_dict = {}

    try:
        for primary_key in primary_keys:
            # Execute SELECT query for each primary key
            cursor.execute('SELECT fx FROM records WHERE x = ?', (primary_key,))
            result = cursor.fetchone()

            if result:
                # 'fx' is in the first element of the tuple
                fx_json = result[0]
                fx_dict = json.loads(fx_json)  # Convert JSON string back to dictionary
                results_dict[primary_key] = fx_dict
            else:
                print(f"No record found for primary key '{primary_key}'")
                results_dict[primary_key] = None  # or handle as needed

    except sqlite3.Error as e:
        print(f"Error fetching records: {e}")

    finally:
        # Close connection
        conn.close()

    return results_dict


def free_cancellation_param(free_cancellation_until):
    datetime_object = datetime.strptime('2024-07-21T11:00:00', '%Y-%m-%dT%H:%M:%S') - datetime.utcnow()
    return datetime_object.days * 24


def get_hotel_offers(response):
    all_hotels = response['data']['hotels']
    static_params = fetch_records([h['id'] for h in response['data']['hotels']])
    hotels_raw = find_hotels_by_ids([hr['id'] for hr in response['data']['hotels']])
    params = [{
                  'daily_prices_sum':
                      sum([float(x) for x in offer['daily_prices']]),
                  'is_meal':
                      True if offer['meal'] != 'nomeal' else False,
                  'price_with_all_taxes':
                      sum([float(taxes['amount']) if taxes['included_by_supplier'] == False else 0 for taxes in
                           offer['payment_options']['payment_types'][0]['tax_data']['taxes']]) + float(
                          offer['payment_options']['payment_types'][0]['commission_info']['charge']['amount_gross']),
                  'free_cancellation_parameter':
                      0 if offer['payment_options']['payment_types'][0]['cancellation_penalties'][
                               'free_cancellation_before'] == None else free_cancellation_param(
                          offer['payment_options']['payment_types'][0]['cancellation_penalties'][
                              'free_cancellation_before']),
                  'indexes':
                      (h_index, o_index),
                  'reception_opens':
                      hotels_raw[hotel['id']]['front_desk_time_start'],
                  'reception_closes': hotels_raw[hotel['id']]['front_desk_time_end']

              } | static_params[hotel['id']]
              for h_index, hotel in enumerate(all_hotels) for o_index, offer in enumerate(hotel['rates'])]
    return pd.DataFrame(params)


def is_reception_open(opening_time=None, closing_time=None, check_time=None):
    # Default opening and closing times if not provided
    opening_time = opening_time or time(6, 0)  # Default opening time: 06:00
    closing_time = closing_time or time(0, 0)  # Default closing time: 00:00 (midnight)

    # If no specific time is provided, use the current time
    if check_time is None:
        check_time = datetime.now().time()

    # If opening time and closing time are the same, reception is open 24 hours
    if opening_time == closing_time:
        return True

    # General case
    if closing_time > opening_time:
        # Reception is open between opening and closing on the same day
        return opening_time <= check_time < closing_time
    else:
        # Reception is open from opening time to midnight, and from midnight to closing time next day
        return check_time >= opening_time or check_time < closing_time


def open_hotels(ticket, pd_hotels, city_coordinates):
    arrival = datetime.strptime(ticket['itineraries'][0]['segments'][-1]['arrival']['at'],
                                "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=60)
    for index in range(len(pd_hotels)):
        if pd_hotels.loc[index, 'reception_opens']:
            reception_open_time = datetime.strptime(pd_hotels.loc[index, 'reception_opens'], "%H:%M:%S").time()
        else:
            reception_open_time = time(6, 0)

        if pd_hotels.loc[index, 'reception_closes']:
            reception_closes_time = datetime.strptime(pd_hotels.loc[index, 'reception_closes'], "%H:%M:%S").time()
        else:
            reception_closes_time = time(0, 0)
        valid_time = is_reception_open(opening_time=reception_open_time, closing_time=reception_closes_time,
                                       check_time=arrival.time())
        pd_hotels.loc[index, 'valid_time'] = valid_time
    result = pd_hotels[pd_hotels['valid_time'] == True].copy().replace({True: 1, False: 0})
    all_coordinates = [(latitude, longitude) for latitude, longitude in zip(result['latitude'], result['longitude'])]
    distances = hs.haversine_vector(array2=city_coordinates, array1=all_coordinates, comb=True).T
    result.loc[:, 'distance_from_city_center'] = distances
    return result[hotels_parameters_list]
