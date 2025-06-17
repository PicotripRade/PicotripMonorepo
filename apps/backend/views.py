# views.py
import ast
import json
import os

from io import StringIO

import h3
import requests
import urllib3
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

from .support_fun import get_result, nearby_airports, get_activity_recommendations
from .tasks import get_destinations # Import the Celery task function

import logging
import polars as pl
import haversine as hs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .models import UserSearch

logger = logging.getLogger('django')

timeout_value = 60 * 60  # Cache for 1 hour

# Load environment variables from .env file
load_dotenv()

# fetches list of available airports after the user starts typing into origin field
@csrf_exempt
def autocomplete_api(request):
    # Extract the string query parameter from the request
    query_string = request.GET.get('input', '')  # Default to empty string if not provided

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "raw_files/worldcitiesh3.parquet")

    cities_raw = pl.read_parquet(file_path)
    df = cities_raw.select('city_ascii', 'id', 'country', 'h3_index_0', 'h3_index_1', 'h3_index_2', 'h3_index_3',
                           'h3_index_4', 'h3_index_5', 'h3_index_6')

    # Determine Elasticsearch password based on WORKMODE
    workmode = os.getenv("VITE_WORKMODE", "DEV")
    if workmode.upper() == "PROD":
        password = "MCNCMhwigWK+1PD0svS5"
    else:
        password = "rade123"

    es = Elasticsearch(
        "http://127.0.0.1:9200",
        basic_auth=("elastic", password),
        verify_certs=False,
    )

    INDEX_NAME = "cities"

    # Check if we should recreate the index

    RECREATE_INDEX = False

    # Only create index if it doesn't exist or if we explicitly want to recreate it
    if RECREATE_INDEX:
        if es.indices.exists(index=INDEX_NAME):
            es.indices.delete(index=INDEX_NAME)

        # Create index with edge_ngram tokenizer
        es.indices.create(index=INDEX_NAME, body={
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "edge_ngram_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 10,
                            "token_chars": ["letter"]
                        }
                    },
                    "analyzer": {
                        "custom_edge_ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "edge_ngram_tokenizer",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "city_ascii": {
                        "type": "text",
                        "analyzer": "custom_edge_ngram_analyzer"
                    }
                }
            }
        })

        actions = [
            {
                "_index": INDEX_NAME,
                "_id": row["id"],
                "_source": row
            }
            for row in df.to_dicts()
        ]

        helpers.bulk(es, actions)
        logger.info("Indexing complete.")

    def search_city_ids(query: str):
        """
        Efficiently search for city ids using the substring query.
        If query length <= 3, use standard tokenizer.
        If query length >= 4 and no results, use fuzzy tokenizer.
        """
        base_query = {
            "_source": ["id"],  # Only fetch 'id' field
            "query": {
                "match": {
                    "city_ascii": {
                        "query": query,
                        "operator": "and"
                    }
                }
            },
            "sort": [{"_score": {"order": "desc"}}]  # Sort by relevance score in descending order
        }

        # Check the query length and decide whether to use fuzziness
        if len(query) >= 4:
            base_query["query"]["match"]["city_ascii"]["fuzziness"] = "1"

        response = es.search(index=INDEX_NAME, body=base_query)
        hits = response['hits']['hits']

        # If no results for query >=4, use fuzzy search
        if not hits and len(query) >= 4:
            fuzzy_query = {
                "_source": ["id"],  # Fetch only 'id' field
                "query": {
                    "match": {
                        "city_ascii": {
                            "query": query,
                            "fuzziness": "1"
                        }
                    },

                },
                "size": 20,
                "sort": [{"_score": {"order": "desc"}}]  # Sort by score for fuzzy match
            }
            response = es.search(index=INDEX_NAME, body=fuzzy_query)
            hits = response['hits']['hits']

        # Return just the list of ids (sorted by highest score first)
        return [hit["_source"]["id"] for hit in hits]

    indexed_cities = cities_raw.filter(pl.col('id').is_in(search_city_ids(query_string)))
    json_results = indexed_cities.to_dicts()
    results = [
        {'city': city['city_ascii'], 'country': city['country'], 'admin_name': city['admin_name'], 'id': city['id']} for
        city in json_results[0:10]]

    # Return the response as JSON
    return JsonResponse({'message': results})


@csrf_exempt
def save_user_search(request):
    if request.method == 'POST':
        try:
            # Extract data from request.session
            task_id = request.COOKIES.get('task_id')

            cache_key = f'session_data_{task_id}'

            search_query = cache.get(f'{cache_key}_request_params')  # Assuming you have a 'search_query' in session
            logger.info("search_query ", search_query)

            activity_tag = cache.get(f'{cache_key}_activity_tag')
            logger.info("activity_tag", activity_tag)

            picked_countries = cache.get(f'{cache_key}_picked_countries_refined')
            picked_cities = cache.get(f'{cache_key}_picked_cities')

            # Create an instance of UserSearch model
            user_search = UserSearch(task_id=task_id, search_query=search_query, activity_tag=activity_tag,
                                     picked_countries=picked_countries, picked_cities=picked_cities)
            logger.info("Saving user search")

            # Save the instance to the database
            user_search.save()

            return JsonResponse({'message': 'User search saved successfully'})
        except:
            logger.error("There was an error saving the search")
            return JsonResponse({'message': 'There was an error saving the search'})
    else:
        return JsonResponse({'error': 'POST method required'})


@csrf_exempt
def set_geolocation(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            raw_coordinates = json.loads(request.body.decode('utf-8'))
            coordinates = ast.literal_eval(raw_coordinates)

            logger.info(f"Coordinates: {coordinates}")

            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(BASE_DIR, "raw_files/worldcitiesh3.parquet")

            cities_raw = pl.read_parquet(file_path)

            my_city = nearest_city(coordinates, cities_raw)

            # Return a success response
            return JsonResponse({'message': 'Geolocation set successfully!', 'city': my_city})
        except Exception as e:
            logger.error(f"Error parsing geolocation: {str(e)}")
            return JsonResponse({'message': 'There was an error setting geolocation'}, status=400)
    else:
        # Return a response for non-POST requests
        return JsonResponse({'message': 'This endpoint only accepts POST requests.'}, status=405)


@csrf_exempt
@require_GET
def get_trip_info(request):
    try:
        # Extract query parameters
        from_location = request.GET.get('from', '')
        begin_date = request.GET.get('begin', '')
        end_date = request.GET.get('end', '')
        activity_type = request.GET.get('activityType', '')
        selected_airports = request.GET.get('selectedAirports', '')

        logger.info("selected airports iata codes")
        logger.info(selected_airports)

        airports = [item.strip() for item in selected_airports.split(",") if item.strip()]

        # Validate required parameters
        # if not all([from_location, begin_date, end_date]):
        #     return JsonResponse(
        #         {'error': 'Missing required parameters: from, begin, end'},
        #         status=400
        #     )

        search_params = {
            "id": from_location,
            "start_date_string": begin_date,
            "end_date_string": end_date,
            "activity_tag": activity_type,
            "airports": airports,
        }


        results = get_result(search_params)
        logger.info("rezultati ful", results)


        logger.info(
            f"Trip info request - From: {from_location}, "
            f"Begin: {begin_date}, End: {end_date}, "
            f"Activity: {activity_type}"
        )

        return JsonResponse({'results': results})

    except Exception as e:
        logger.error(f"Error processing trip info request: {str(e)}")
        return JsonResponse(
            {'error': 'Internal server error'},
            status=500
        )


@csrf_exempt
def get_user_location_initial(request):
    try:
        # Parse the request body
        ip_address = get_client_ip(request)

        # For development, you might want to use a test IP
        if ip_address == '127.0.0.1':
            # Use a sample IP or mock response for development
            ip_address = '8.8.8.8'  # Google's public DNS as example

        ip_addr_mock = '109.245.205.77'
        # Using ip-api.com (free tier available)
        workmode = os.getenv("VITE_WORKMODE", "DEV")
        if workmode.upper() == "PROD":
            response = requests.get(f'http://ip-api.com/json/{ip_address}')
        else:
            response = requests.get(f'http://ip-api.com/json/{ip_addr_mock}')

        data = response.json()
        logger.info("data", data)
        logger.info(data['city'])

        if data.get('status') == 'success':
            logger.info("success in fetching location")

            lat = data['lat']
            lon = data['lon']

            coordinates = (lat, lon)

            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(BASE_DIR, "raw_files/worldcitiesh3.parquet")

            cities_raw = pl.read_parquet(file_path)
            new_data = nearest_city(coordinates, cities_raw)
            logger.info("raw data returned")
            logger.info(new_data)
            return JsonResponse({'city': new_data['city'], "country": new_data['country'], "id" :new_data['id']})
        else:
            return JsonResponse({'error': 'Could not determine location', 'ip': ip_address}, status=400)
    except Exception as e:
        logger.error(f"Error parsing geolocation: {str(e)}")
        return JsonResponse({'message': 'There was an error setting geolocation'}, status=400)


# Helper functions
def extract_airport_code(location):
    # The format is expected to be "City (CODE)"
    # Use regex to extract the code between parentheses
    import re
    match = re.search(r'\((\w{3})\)', location)
    if match:
        return match.group(1)
    return location  # Return the original string if the format is not as expected


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
def get_airports_list(request):
    city_id_extracted = request.GET.get('city_id', '')
    search_params = {
        "id": int(city_id_extracted),
        "start_date_string": "2025-10-15",
        "end_date_string": "2025-10-22",
        "activity_tag": "summer",
    }
    logger.info("search_params in get airports", search_params)

    airports_list = nearby_airports(search_params).select(['iata_code','name','iso_country']).to_dicts()

    return JsonResponse(airports_list, safe=False)

@csrf_exempt
def get_city_info(request):
    try:
        city_id_extracted = request.GET.get('geoname', '')
        from_location = request.GET.get('from', '')
        begin_date = request.GET.get('begin', '')
        end_date = request.GET.get('end', '')
        activity_type = request.GET.get('activityType', '')
        selected_airports = request.GET.get('selectedAirports', '')
        transport_type = request.GET.get('transportType', '')
        city_name = request.GET.get('cityName', '')
        country_name = request.GET.get('countryName', '')

        search_params = {
            "id": from_location,
            "start_date_string": begin_date,
            "end_date_string": end_date,
            "activity_tag": activity_type,
            "city_id": city_id_extracted,
            "transport_type": transport_type,
            "city_name": city_name,
            "country_name": country_name,
        }
        response = get_activity_recommendations(start_date=begin_date, end_date=end_date, activity=activity_type,
                                                destination_city=city_name, destination_state=country_name, transport_type=transport_type)

        logger.info("search_params in get city info")
        logger.info(search_params)

        return JsonResponse(response, safe=False)
    except Exception as e:
        logger.error(f"Error parsing geolocation: {str(e)}")
        return JsonResponse({'message': 'There was an error processing request'}, status=500)



def nearest_city(coordinates, autocomplete_cities):
    allowed_indexes = [(6, 0), (6, 1), (5, 0), (5, 1), (4, 0), (4, 1), (3, 0), (3, 1)]
    for h3_index_radius in allowed_indexes:
        autocomplete_city_index = h3.latlng_to_cell(coordinates[0], coordinates[1], h3_index_radius[0])
        grid_disk = h3.grid_disk(autocomplete_city_index, h3_index_radius[1])
        found_cities = autocomplete_cities.filter(pl.col(f'h3_index_{h3_index_radius[0]}').is_in(grid_disk))
        if found_cities.height != 0:
            break
        else:
            pass
    found_list = list(zip(found_cities["lat"], found_cities["lng"]))
    distances = hs.haversine_vector(coordinates, found_list, comb=True).flatten().tolist()
    found_cities = \
        found_cities.with_columns(pl.Series("distance", distances)).sort(by="distance", descending=False).head(
            1).to_dicts()[0]
    return found_cities
