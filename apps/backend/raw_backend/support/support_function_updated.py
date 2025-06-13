import re
import numpy as np
import json
import requests
from amadeus import Client, ResponseError
import itertools
import concurrent
from concurrent import futures
from .API_Keys import ApiKeys
import logging
from backend.raw_backend.control_panel.HW import budget_cutoff
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
from concurrent.futures import ThreadPoolExecutor, wait
from openai import OpenAI
from groq import Groq
import ast

import pickle
import pandas as pd
from datetime import datetime, timedelta, time
from .support_objects import country_names
from ..control_panel.HW import hotel_weights, location_radius, budget_cutoff
from pydantic import BaseModel
from typing import List

with open('backend/raw_backend/support/databases/new_airports.pkl', 'rb') as fp:
    new_airports = pickle.load(fp)

with open('backend/raw_backend/all_reviews.json', 'rb') as fp:
    all_reviews = json.load(fp)

client_openai = OpenAI(api_key=ApiKeys.openai_key)
client_groq = Groq(api_key=ApiKeys.groq_key)

logger = logging.getLogger('django')


class City(BaseModel):
    city_name: str
    final_score: float
    to_visit: List[str]


class ScoringCities(BaseModel):
    cities: List[City]
    final_answer: str


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


# ova funkcija trazi destinacije na za koje postoje direktni letovi za izabrane datume
def connected_destinations(departure_location, departure_date,
                           return_date, one_stop_allowed=True,
                           exclude_llc=True):
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
    # print('results', results)

    if exclude_llc == True:  # ovaj blok smo dodali zato sto zelimo da iskljucimo letove sa lowcosterima (amadeus nam ih  ne daje sem u enterprise paketu)
        excluded_departure = [flight for flight in results[0] if
                              flight['airline']['iataCode'].upper() not in llc_list.keys()]
        excluded_arrival = [flight for flight in results[1] if
                            flight['airline']['iataCode'].upper() not in llc_list.keys()]
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
    # print(destinations)
    all_destinations = []

    for i in destinations['flight_edge']:
        all_destinations.append(i)

    all_destinations = set(all_destinations)
    return all_destinations

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
    all_params.append(list(map(lambda x: int(x['id']) - 1, tickets)))
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
    all_params.append(list(map(lambda x: (int(x[0]['id']) - 1, int(x[1]['id']) - 1), combinations)))
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


def tickets_weights(final_tickets, activity_tag, budget_tag, trip_duration):
    weights = weights_for_flight_tickets(activity_tag, trip_duration, budget_tag)

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
    conn = sqlite3.connect('backend/raw_backend/hotels.db')
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


# def find_hotels_by_ids(hotel_ids):
#     print('u find hotel by ids sam')
#     # Initialize the result dictionary
#     result = {hotel_id: find_hotel_by_id(hotel_id) for hotel_id in hotel_ids}
#     return result

def find_hotels_by_ids(hotel_ids):
    # Connect to SQLite database
    conn = sqlite3.connect('backend/raw_backend/hotels.db')
    cursor = conn.cursor()

    results_dict = {}

    try:
        # Prepare placeholders for the IN clause
        placeholders = ','.join('?' for _ in hotel_ids)

        # Execute SELECT query for all hotel IDs at once
        query = f'SELECT id, data FROM hotels WHERE id IN ({placeholders})'
        cursor.execute(query, hotel_ids)

        # Fetch all results
        results = cursor.fetchall()

        # Process each result
        for hotel_id, json_string in results:
            # Process the JSON string similarly to your original function
            if json_string.endswith('_modified'):
                cleaned_json_string = json_string[:-9]
                cleaned_json_string = json.loads(cleaned_json_string)
            else:
                cleaned_json_string = json.loads(json_string)

            if type(cleaned_json_string) != dict:
                cleaned_json_string = json.loads(cleaned_json_string)

            results_dict[hotel_id] = cleaned_json_string

        # Handle missing hotel IDs by adding them with None as value
        for hotel_id in hotel_ids:
            if hotel_id not in results_dict:
                print(f"No record found for hotel ID '{hotel_id}'")
                results_dict[hotel_id] = None  # or handle as needed

    except sqlite3.Error as e:
        print(f"Error fetching hotels: {e}")
    finally:
        # Close the connection
        conn.close()

    return results_dict


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
    conn = sqlite3.connect('backend/raw_backend/records.db')
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
    conn = sqlite3.connect('backend/raw_backend/records.db')
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

import sqlite3
import json


def fetch_records(primary_keys):
    # Connect to SQLite database
    conn = sqlite3.connect('backend/raw_backend/records.db')
    cursor = conn.cursor()

    results_dict = {}

    try:
        # Prepare placeholders for the IN clause
        placeholders = ','.join('?' for _ in primary_keys)

        # Execute SELECT query for all primary keys at once
        query = f'SELECT x, fx FROM records WHERE x IN ({placeholders})'
        cursor.execute(query, primary_keys)

        # Fetch all results
        results = cursor.fetchall()

        # Convert results to dictionary
        for x, fx_json in results:
            fx_dict = json.loads(fx_json)  # Convert JSON string back to dictionary
            results_dict[x] = fx_dict

        # Handle missing primary keys by adding them with None as value
        for primary_key in primary_keys:
            if primary_key not in results_dict:
                print(f"No record found for primary key '{primary_key}'")
                results_dict[primary_key] = None  # or handle as needed

    except sqlite3.Error as e:
        print(f"Error fetching records: {e}")
    finally:
        # Close the connection
        conn.close()

    return results_dict

    # def fetch_records(primary_keys):


#     # Connect to SQLite database
#     conn = sqlite3.connect('backend/raw_backend/records.db')
#     cursor = conn.cursor()
#
#     results_dict = {}
#
#     try:
#         for primary_key in primary_keys:
#             # Execute SELECT query for each primary key
#             cursor.execute('SELECT fx FROM records WHERE x = ?', (primary_key,))
#             result = cursor.fetchone()
#
#             if result:
#                 # 'fx' is in the first element of the tuple
#                 fx_json = result[0]
#                 fx_dict = json.loads(fx_json)  # Convert JSON string back to dictionary
#                 results_dict[primary_key] = fx_dict
#             else:
#                 print(f"No record found for primary key '{primary_key}'")
#                 results_dict[primary_key] = None  # or handle as needed
#
#     except sqlite3.Error as e:
#         print(f"Error fetching records: {e}")
#
#     finally:
#         # Close connection
#         conn.close()
#
#     return results_dict


def free_cancellation_param(free_cancellation_until):
    datetime_object = datetime.strptime('2024-07-21T11:00:00', '%Y-%m-%dT%H:%M:%S') - datetime.utcnow()
    return datetime_object.days * 24


def get_hotel_offers(ticket, data):
    departure_date = data['departureDate']
    return_date = data['returnDate']
    response = data['hotels']
    coordinates = ast.literal_eval(data['city coor'])
    budget_tag = data['budget_tag']
    days_to_stay = (time_object(return_date) - time_object(departure_date)).days
    activity_tag = data['activity_tag']
    all_hotels = response['data']['hotels']
    static_params = [h['id'] for h in response['data']['hotels']]
    static_params_found = fetch_records(static_params)
    hotels_raw = find_hotels_by_ids(static_params)

    arrival = datetime.strptime(ticket['itineraries'][0]['segments'][-1]['arrival']['at'],
                                "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=60)
    params = [{'indexes':
                   (h_index, o_index),
               'valid_time':
                   is_reception_open(opening_time=datetime.strptime(
                       hotels_raw[hotel['id']]['front_desk_time_start'] if hotels_raw[hotel['id']][
                           'front_desk_time_start'] else "06:00:00", "%H:%M:%S").time(),
                                     closing_time=datetime.strptime(
                                         hotels_raw[hotel['id']]['front_desk_time_end'] if hotels_raw[hotel['id']][
                                             'front_desk_time_end'] else "00:00:00", "%H:%M:%S").time(),
                                     check_time=arrival.time()),
               'daily_prices_sum':
                   sum([float(x) for x in offer['daily_prices']]),
               'distances':
                   hs.haversine(point1=(hotels_raw[hotel['id']]['latitude'], hotels_raw[hotel['id']]['longitude']),
                                point2=coordinates),
               'price_with_all_taxes': sum([float(x) for x in offer['daily_prices']]),  # hotel_taxes(offer),

               'is_meal':
                   True if offer['meal'] != 'nomeal' else False,
               'free_cancellation_parameter':
                   0 if offer['payment_options']['payment_types'][0]['cancellation_penalties'][
                            'free_cancellation_before'] is None else free_cancellation_param(
                       offer['payment_options']['payment_types'][0]['cancellation_penalties'][
                           'free_cancellation_before']),

               } | static_params_found[hotel['id']]
              for h_index, hotel in enumerate(all_hotels) for o_index, offer in enumerate(hotel['rates'])]
    pd_hotel = pd.DataFrame(params)
    pd_hotel['valid_time'] = np.where(pd_hotel['valid_time'], 1, 0)
    pd_hotel['is_meal'] = np.where(pd_hotel['is_meal'], 1, 0)
    pd_hotel = pd_hotel.astype({col: 'float64' for col in pd_hotel.select_dtypes(include='int64').columns})
    # pd_hotel.iloc[:,[3,4,]+[5,6,8,9]+list(range(9,22))+list(range(24,len(pd_hotel.columns)))]=pd_hotel.iloc[:,[3,4,]+[5,6,8,9]+list(range(9,22))+list(range(24,len(pd_hotel.columns)))].astype('float64')

    if len(pd_hotel) > 1:
        if budget_tag == 'Budget':
            pd_hotel = pd_hotel[
                pd_hotel['daily_prices_sum'] < pd_hotel['daily_prices_sum'].quantile(budget_cutoff['Budget'])]
        elif budget_tag == 'Standard':
            pd_hotel = pd_hotel[
                (pd_hotel['daily_prices_sum'].quantile(budget_cutoff['Budget']) < pd_hotel['daily_prices_sum']) & (
                        pd_hotel['daily_prices_sum'] < pd_hotel['daily_prices_sum'].quantile(
                    budget_cutoff['Standard']))]

        else:
            pd_hotel = pd_hotel[
                (pd_hotel['daily_prices_sum'].quantile(budget_cutoff['Standard']) < pd_hotel['daily_prices_sum']) & (
                        pd_hotel['star_rating'] > 3)]
    else:
        pass

    pd_hotel = pd_hotel[pd_hotel['distances'] < location_radius(activity_tag=activity_tag, days_to_stay=days_to_stay,
                                                                picked_budget=budget_tag)]

    # definisemo koje kolone su za score kao i kolone koje daju veci/manji score ukoliko su vrijednosti vise/nize

    param_cols = [3, 4, 5, 6, 8, 9] + list(range(9, 22)) + list(range(24, len(pd_hotel.columns)))
    lb_cols = [3, 4]
    hb_cols = [5, 6, 8, 9] + list(range(9, 22)) + list(range(24, len(pd_hotel.columns)))

    pd_hotel.iloc[:, lb_cols] = pd_hotel.iloc[:, lb_cols].apply(min_max_scaling_lb)
    pd_hotel.iloc[:, hb_cols] = pd_hotel.iloc[:, hb_cols].apply(min_max_scaling_hb)
    pd_hotel = pd_hotel.fillna(0)
    pd_hotel = pd_hotel.infer_objects(copy=False)
    weights = hotel_weights(picked_budget=budget_tag, days_to_stay=days_to_stay)

    pd_hotel = pd_hotel.copy()
    for column in pd_hotel.iloc[:, param_cols].columns:
        if column in list(weights.keys()):
            pd_hotel[column] = pd_hotel[column] * weights[column]
        else:
            pd_hotel[column] = 0

    selected_columns = pd_hotel.iloc[:, param_cols]
    pd_hotel = pd.concat([pd_hotel, selected_columns.sum(axis=1).rename('score')], axis=1)
    pd_hotel = pd_hotel.sort_values(by=['score'], ascending=True)
    final_offer = pd_hotel[pd_hotel['valid_time'] == 1].groupby(pd_hotel['indexes'].apply(lambda x: x[0])).head(
        1).copy()
    hotel_indexes = [x for x in list(final_offer.iloc[:min(3, len(final_offer)), 0])]
    # POPRAVI SOBU ZA NAJBOLJU PONUDU
    try:
        final_dict = [{'dynamic_data': data['hotels']['data']['hotels'][index[0]]['rates'][index[1]],
                       'static_data': find_hotel_by_id(data['hotels']['data']['hotels'][index[0]]['id'])} for index in
                      hotel_indexes]
    except:
        print('ne radi final dict')

    return final_dict


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


def rate_hawk_geo_api(checkin,
                      checkout,
                      adults,
                      children,
                      latitude,
                      longitude,
                      language='en',
                      currency='EUR',
                      residency=None,
                      radius=15000
                      ):
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
        "latitude": latitude,
        "longitude": longitude,  # 42.1354° N, 24.7453° E
        "radius": radius,  # in meters from center of the city
        "currency": currency,
        "residency": residency
    })
    headers = {
        'Content-Type': 'application/json'
    }
    auth = (ApiKeys.RateHawk_api_secret, ApiKeys.RateHawk_api_key)
    response_hotels = requests.request("POST", url, headers=headers, data=payload, auth=auth).json()
    return response_hotels


def raw_tickets(request_params):
    destination = request_params['airport']
    origin = request_params['departureLocation']
    departure_date = request_params['departureDate']
    return_date = request_params['returnDate']
    adults = request_params['adults']
    children = request_params['children']
    trip_duration = (time_object(return_date) - time_object(departure_date)).days

    checked_bags_only = is_baggage_required(trip_duration=trip_duration)

    #  Pozivamo amadeus post request sa parametrima koje imamo sa frontenda
    tickets = amadeus_post(origin=origin, destination=destination, adults=adults, children=children,
                           max_number_of_connections=1, checked_bags_only=checked_bags_only, add_one_way_offers='true',
                           departure_date=departure_date, return_date=return_date)
    return tickets


def filter_hotels(hotels_response):
    conn = sqlite3.connect('backend/raw_backend/hotels.db')
    cursor = conn.cursor()

    ids = [hotel['id'] for hotel in hotels_response['data']['hotels']]

    query = 'SELECT * FROM hotels WHERE id IN ({seq})'.format(
        seq=','.join(['?'] * len(ids))
    )

    # Execute the query
    cursor.execute(query, ids)

    # Fetch all matching records
    records = cursor.fetchall()

    # raw_hotel_data_dict = {record[0]:clear_string(record[1]) for record in records}
    # dynamic_hotel_data_dict = {hotel['id']: hotel for hotel in hotels_response['data']['hotels']}
    # hotel_vectors = fetch_records_by_keys(ids)
    # final_data = [{'hotel_id': key , 'static_data':raw_hotel_data_dict[key], 'dynamic_data': dynamic_hotel_data_dict[key], 'hotel_vector': json.loads(hotel_vectors[key])} for key in list(raw_hotel_data_dict.keys())]
    list_of_avaliable_hotels = [record[0] for record in records]
    filtered = [k for k in hotels_response['data']['hotels'] if k['id'] in list_of_avaliable_hotels]
    hotels_response['data']['hotels'] = filtered
    return hotels_response


def get_raw_offer_data(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tickets = executor.submit(raw_tickets, data)
        hotels = executor.submit(rate_hawk_geo_api, checkin=data['departureDate'], checkout=data['returnDate'],
                                 adults=data['adults'], children=data['children'],
                                 latitude=ast.literal_eval(data['city coor'])[0],
                                 longitude=ast.literal_eval(data['city coor'])[1])

        concurrent.futures.wait([tickets, hotels])

        json_data = json.dumps({'flight_tickets': tickets.result(), 'all_hotels': filter_hotels(hotels.result())})
    return json_data


def get_optimal_ticket(data):
    destination = data['airport']
    origin = data['departureLocation']
    departure_date = data['departureDate']
    return_date = data['returnDate']
    activity_tag = data['activity_tag']
    trip_duration = (time_object(return_date) - time_object(departure_date)).days
    tickets = data['tickets']
    budget = data['budget_tag']

    #  Pravimo dataframe za kombinovane karte
    combos = combo_df(tickets=tickets, origin=origin, destination=destination, departure_date=departure_date,
                      return_date=return_date)
    #  Pravimo dataset za povratne karte
    return_tickets = return_df(tickets=tickets, origin=origin, destination=destination, departure_date=departure_date,
                               return_date=return_date)
    #  Spajamo sve karte
    final_tickets = pd.concat([combos, return_tickets], ignore_index=True)
    result = tickets_weights(final_tickets=final_tickets, activity_tag=activity_tag, budget_tag=budget,
                             trip_duration=trip_duration)
    result = result.groupby('stay on location score').head(1)
    final_result = result.sort_values('total score', ascending=False).iloc[:min(3, len(result)), :]
    tickets_indexes = list(final_result['id'])
    delivery = [
        [tickets[ticket] for ticket in single_or_combined_tickets] if type(single_or_combined_tickets) == tuple else [
            tickets[single_or_combined_tickets]] for single_or_combined_tickets in tickets_indexes]
    return delivery


def hotel_taxes(offer):
    try:
        tax = float(offer['payment_options']['payment_types'][0]['commission_info']['charge'][
                        'amount_gross'])  # + sum([float(taxes['amount']) if taxes['included_by_supplier']==False else 0 for taxes in offer['payment_options']['payment_types'][0]['tax_data']['taxes']])
    except:
        tax = float(offer['payment_options']['payment_types'][0]['commission_info']['charge']['amount_gross'])
    return tax


def get_optimal_hotel_ticket(data):
    try:
        optimal_tikcets = get_optimal_ticket(data=data)
    except:
        optimal_tikcets = 'no valid ticket found'
        print('karte ne rade')
    try:
        optimal_hotels_regarding_ticket = [(ticket, get_hotel_offers(data=data, ticket=ticket[0])) for ticket in
                                           optimal_tikcets]
    except:
        optimal_hotels_regarding_ticket = 'no hotels found on the location'

    return optimal_hotels_regarding_ticket


def mean_coord(list_of_coord):
    unzipped_lists = list(zip(*list_of_coord))

    mean_values = [sum(lst) / len(lst) for lst in unzipped_lists]

    return tuple(mean_values)


def filter_hotels(hotels_response):
    conn = sqlite3.connect('backend/raw_backend/hotels.db')
    cursor = conn.cursor()

    ids = [hotel['id'] for hotel in hotels_response['data']['hotels']]

    query = 'SELECT * FROM hotels WHERE id IN ({seq})'.format(
        seq=','.join(['?'] * len(ids))
    )

    # Execute the query
    cursor.execute(query, ids)

    # Fetch all matching records
    records = cursor.fetchall()

    # raw_hotel_data_dict = {record[0]:clear_string(record[1]) for record in records}
    # dynamic_hotel_data_dict = {hotel['id']: hotel for hotel in hotels_response['data']['hotels']}
    # hotel_vectors = fetch_records_by_keys(ids)
    # final_data = [{'hotel_id': key , 'static_data':raw_hotel_data_dict[key], 'dynamic_data': dynamic_hotel_data_dict[key], 'hotel_vector': json.loads(hotel_vectors[key])} for key in list(raw_hotel_data_dict.keys())]
    list_of_avaliable_hotels = [record[0] for record in records]
    filtered = [k for k in hotels_response['data']['hotels'] if k['id'] in list_of_avaliable_hotels]
    hotels_response['data']['hotels'] = filtered
    return hotels_response


def transfer_time_arrival(date_time_str):
    # Parse the string into a datetime object
    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')

    # Subtract 2.5 hours (which is equivalent to 2 hours and 30 minutes)
    new_date_time_obj = date_time_obj + timedelta(hours=0, minutes=45)

    # Convert the datetime object back into a string in the same format
    new_date_time_str = new_date_time_obj.strftime('%Y-%m-%dT%H:%M:%S')

    return new_date_time_str


def transfer_time_departure(date_time_str):
    # Parse the string into a datetime object
    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')

    # Subtract 2.5 hours (which is equivalent to 2 hours and 30 minutes)
    new_date_time_obj = date_time_obj - timedelta(hours=2, minutes=30)

    # Convert the datetime object back into a string in the same format
    new_date_time_str = new_date_time_obj.strftime('%Y-%m-%dT%H:%M:%S')

    return new_date_time_str


def extract_params_for_transfer(data):
    try:
        search_params = {'latitude': data['data'][0][1][0]['static_data']['latitude'],
                         'longitude': data['data'][0][1][0]['static_data']['longitude'],
                         'hotel_address': data['data'][0][1][0]['static_data']['address'],
                         'start_time_to_hotel': transfer_time_arrival(
                             data['data'][0][0][0]['itineraries'][0]['segments'][-1]['arrival']['at']),
                         'start_time_to_airport': transfer_time_departure(
                             data['data'][0][0][-1]['itineraries'][-1]['segments'][0]['departure']['at']),
                         'pick_up_airport': data['data'][0][0][0]['itineraries'][0]['segments'][-1]['arrival'][
                             'iataCode'],
                         'no_of_passingers': len(data['data'][0][0][0]['travelerPricings']),
                         'hotel_postal_code': data['data'][0][1][0]['static_data']['postal_code'],
                         'country_code': data['data'][0][1][0]['static_data']['region']['country_code'],
                         'city_name': data['data'][0][1][0]['static_data']['region']['name']

                         }
    except:
        search_params = 'no_transfer'

    return search_params


def get_transfer_to_origin(picked_location):
    amadeus = Client(
        client_id=ApiKeys.amadeus_api_key,
        client_secret=ApiKeys.amadeus_api_secret,
        hostname='production'
    )
    budget = picked_location['budget']
    data = {
        "startDateTime": picked_location['start_time_to_airport'],
        "passengers": picked_location['no_of_passingers'],
        # "startLocationCode": 'BEG',
        "startAddressLine": picked_location['hotel_address'],
        "startZipCode": picked_location['hotel_postal_code'],
        "startCountryCode": picked_location['country_code'],
        "startCityName": picked_location['city_name'],
        # "startStateCode": "string",
        "startGeoCode": f'{picked_location["latitude"]},{picked_location["longitude"]}',
        # "startName": "place name e.g. Airport Name, Hotel Name etc.",
        "endLocationCode": picked_location['pick_up_airport'],
        # example: CDG
        # "endAddressLine": "Blågårdsgade 26, 2200 København N, Denmark",
        # "endZipCode":	picked_location[0][1][0]['static_data']['postal_code'],
        # "endCountryCode": "string",
        "endCityName": "string",
        "endStateCode": picked_location['country_code'],
        # "endGeoCode": "44.80695585816261, 20.482635668703555",
        # "endName": picked_location[0][1][0]['static_data']['name'],
        # "transferType": "TAXI",
        # "duration":	"PT3H10M",
        "language": "EN",
        "currency": "EUR",
        # "vehicleCode": "BUS"
        # "startConnectedSegment": 1,
        # "endConnectedSegment": 1,
    }

    json_string = json.dumps(data, indent=4)

    body = json.loads(json_string)
    try:
        response = amadeus.shopping.transfer_offers.post(body)

    except ResponseError as error:
        raise error
        print(error)

    return response.data


def get_transfer_to_dest(picked_location):
    amadeus = Client(
        client_id=ApiKeys.amadeus_api_key,
        client_secret=ApiKeys.amadeus_api_secret,
        hostname='production'
    )
    budget = picked_location['budget']
    data = {
        "startDateTime": picked_location['start_time_to_hotel'],
        "passengers": picked_location['no_of_passingers'],
        "startLocationCode": picked_location['pick_up_airport'],
        # "startAddressLine" : 1,
        # "startZipCode" : 1,
        # "startCountryCode":	"string",
        # "startCityName": "string",
        # "startStateCode": "string",
        # "startGeoCode": "Example: 48.858093,2.294694",
        # "startName": "place name e.g. Airport Name, Hotel Name etc.",
        # "endLocationCode":	"string",
        # example: CDG
        "endAddressLine": picked_location['hotel_address'],
        "endZipCode": picked_location['hotel_postal_code'],
        # "endCountryCode": "string",
        # "endCityName":	"string",
        # "endStateCode": "string",
        "endGeoCode": f'{picked_location["latitude"]},{picked_location["longitude"]}',
        # "endName": picked_location[0][1][0]['static_data']['name'],
        # "transferType": "TAXI",
        # "duration":	"PT3H10M",
        "language": "EN",
        "currency": "EUR",
        # "vehicleCode": "BUS"
        # "startConnectedSegment": 1,
        # "endConnectedSegment": 1,
    }

    json_string = json.dumps(data, indent=4)

    body = json.loads(json_string)
    try:
        response = amadeus.shopping.transfer_offers.post(body)

    except ResponseError as error:
        raise error
        print(error)

    return response.data


def optimal_transfer(transfers, budget):
    prices = [float(taxi['quotation']['monetaryAmount']) for taxi in transfers]
    if budget == 'lux':
        cutoff_value = np.percentile(prices, 60)
        filtered = [(i, num) for i, num in enumerate(prices) if num >= cutoff_value]
    else:
        cutoff_value = np.percentile(prices, 20)
        filtered = [(i, num) for i, num in enumerate(prices) if num <= cutoff_value]

    # Sort the filtered list by the values in ascending order
    sorted_filtered = sorted(filtered, key=lambda x: x[1])

    # Return the first member of the sorted list (index, value pair)
    if sorted_filtered:
        return transfers[sorted_filtered[0][0]]
    else:
        return None  # Return None if no values are above the cutoff


def get_transfers(data, budget):
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit the functions to the executor
        future1 = executor.submit(get_transfer_to_dest, data)
        future2 = executor.submit(get_transfer_to_origin, data)

        # Wait until both functions are complete
        done, not_done = wait([future1, future2])

        # Fetch results only after both functions are done
        result1 = future1.result()
        result2 = future2.result()

    transfer_to_hotel = optimal_transfer(transfers=result1, budget=budget)
    transfer_to_origin = optimal_transfer(transfers=result2, budget=budget)
    return {'transfer_to_hotel': transfer_to_hotel, 'transfer_to_origin': transfer_to_origin}


def filter_prices(offer):
    arrival = offer['data'][0][0][0]['itineraries'][0]['segments'][-1]['arrival']['at']
    departure = offer['data'][0][0][-1]['itineraries'][-1]['segments'][0]['departure']['at']

    arrival_date = datetime.strptime(arrival, '%Y-%m-%dT%H:%M:%S')
    departure_date = datetime.strptime(departure, '%Y-%m-%dT%H:%M:%S')

    nights_needed = (departure_date - arrival_date).days
    nights_response = len(offer['data'][0][1][0]['dynamic_data']['daily_prices'])
    difference = nights_response - nights_needed
    if difference > 0:
        for i in range(len(offer['data'][0][1])):
            for j in range(len(offer['data'])):
                offer['data'][0][1][i]['dynamic_data']['daily_prices'] = offer['data'][0][1][i]['dynamic_data'][
                                                                             'daily_prices'][
                                                                         difference:]
    else:
        pass

    return offer


def prompt_top_cities(data, number_of_top_scored=10, model="gpt-4o-mini", temperature=0.01, top_p=1,
                      response_format=ScoringCities):
    departure_date = data['departureDate']
    return_date = data['returnDate']
    adults = data['adults']
    children = data['children']
    model = model
    cities_list = data['cities_list']
    days_on_trip = data['days_on_trip']
    activity_tag = data['activity_tag']  # u ovom slucaju mora biti ekspresivan tag npr: 'relaxing family trip'
    if activity_tag == 'summer_vacation':
        activity_tag_description = 'having good, relaxing holiday on place good for swimming, outdoor activiteies and sunny weather'
    else:
        activity_tag_description = 'outdoor activiteies and sunny weather'

    if activity_tag == 'summer_vacation' and days_on_trip >= 4:
        desirable_activities_list = ['swimming', 'water sports', 'nightlife']  # ovo je bino!!!
        recommandation_list = ['less crowded, exotic beaches',]  # # ovo je bino!!!
        ideal_weather = 'sunny'
        crowdedness_parameter = 'more'
        messages = [
            {"role": "system",
             "content": f"you are touristic expert and you are help me to choose best destinations for {activity_tag_description}. you will be provided by list of locations, and you have to score every city from 0-100 for: following parameters :"
                        f"1.Place good for activities such as {desirable_activities_list}, for {adults} adults and {children} children, between dates {departure_date} and {return_date}."
                        f"2. {ideal_weather} weather probability (higher is better) calculated on historic data for the dates on the location."
                        f"3.crowdedness  of the location on the dates ({crowdedness_parameter} crowded is better)."
                        f"-Calculate mean value of scores (1-3) for every location to get final_score. Return JSON format of up to top {number_of_top_scored} cities by  final_score. Also make 'to_visit' list of some (not necessary all) places of type {recommandation_list}"},
            {"role": "user", "content": f"{cities_list}"}]
    else:
        desirable_activities_list = ['biking']
        recommandation_list = ['good pizza restaurants', 'national cusine restaurant']
        ideal_weather = 'dry'
        crowdedness_parameter = 'less'
        messages = [
            {"role": "system",
             "content": f"you are touristic expert and you are help me to choose best destinations for {activity_tag}. you will be provided by list of locations, and you have to score every city from 0-100 for: following parameters :"
                        f"1.Place good for activities such as {desirable_activities_list}, for {adults} adults and {children} children, between dates {departure_date} and {return_date}."
                        f"2. {ideal_weather} weather probability (higher is better) calculated on historic data for the dates on the location."
                        f"3.crowdedness  of the location on the dates ({crowdedness_parameter} crowded is better)."
                        f"-Calculate mean value of scores (1-3) for every location to get final_score. Return JSON format of top {number_of_top_scored} cities by  final_score. Also make 'to_visit' list of some (not necessary all) places of type {recommandation_list}"},
            {"role": "user", "content": f"{cities_list}"}]

    completion = client_openai.beta.chat.completions.parse(model=model, messages=messages,
                                                           response_format=response_format, top_p=top_p,
                                                           temperature=temperature)
    scoring_cities = json.loads(completion.choices[0].message.content)
    return scoring_cities


def data_cutter(optimal_offer):
    for destination in optimal_offer:
        if destination['data'] == "no hotels found on the location":
            logger.error(destination['data'])
            continue
        else:
            for offer in destination['data']:
                try:
                    for hotel in offer[1]:
                        dynamic_room = hotel['dynamic_data']['rg_ext']
                        if type(hotel['static_data']['room_groups']) is list:
                            for room in hotel['static_data']['room_groups']:
                                if room == dynamic_room:
                                    hotel['static_data']['room_groups'] = dynamic_room
                                else:
                                    pass
                        else:
                            pass
                except:
                    logger.error("Issue extracting hotel data. ", offer)
                    print("Issue extracting hotel data. ", offer)
            return optimal_offer


def convert_df_coordinates(df):
    try:
        df['city coor'] = df['city coor'].apply(ast.literal_eval)
        tuple_coordinates = df.copy()
    except:
        logger.error(" converting coordinates ", df)
        return df
    return tuple_coordinates


def chain_funcs(filters_list, data_frame, activity_tag):
    result = data_frame
    for func in filters_list:
        result = func(result, activity_tag)  # Passing both arguments to each function
    return result


def include_area(df, min_max_coordinates_list):  # (min_lat,max_lat,min_lon,max_lon). planet Earth  - (-90,90,-180,180)

    filtered_dfs = []
    for area in min_max_coordinates_list:
        filtered_dfs.append(df[
                                (df['city coor'].apply(lambda x: x[0] > area[0]))
                                & (df['city coor'].apply(lambda x: x[0] < area[1]))
                                & (df['city coor'].apply(lambda x: x[1] > area[2]))
                                & (df['city coor'].apply(lambda x: x[1] < area[3]))])
    filtered = pd.concat(filtered_dfs)
    return filtered

def exclude_area(df, min_max_coordinates_list):  # (min_lat,max_lat,min_lon,max_lon). planet Earth  - (-90,90,-180,180)

    filtered_dfs = []
    for area in min_max_coordinates_list:
        filtered_dfs.append(df[~(
                                (df['city coor'].apply(lambda x: x[0] > area[0]))
                                & (df['city coor'].apply(lambda x: x[0] < area[1]))
                                & (df['city coor'].apply(lambda x: x[1] > area[2]))
                                & (df['city coor'].apply(lambda x: x[1] < area[3])))])
    filtered = pd.concat(filtered_dfs)
    return filtered