# tasks.py (inside your Django app)

import json

from .raw_backend.support.support_function_updated import get_raw_offer_data, get_transfers
import logging
from backend.celery import app as celery_app

logger = logging.getLogger('django')

from celery import shared_task
from .raw_backend.UserInput import UserInput
from .raw_backend.PosibleDestinations import Destinations
from .raw_backend.DistanceFilter import DistanceFilter
task_timeout = 1800

@shared_task(time_limit = task_timeout)
def get_destinations(data):
    user_input = UserInput(data=data)
    try:
        possible_destinations = Destinations(user_input)
        distance_filter = DistanceFilter(possible_destinations, user_input).distance_filtered
    except Exception as e:
        logger.exception("Exception occurred when trying to get destinations: %s", e)
        distance_filter = {}
        return distance_filter
    return distance_filter.to_json(orient='split')


@celery_app.task(time_limit = task_timeout)
def get_offers(data):
    raw_data = get_raw_offer_data(data)
    tickets = json.loads(raw_data)['flight_tickets']
    hotels = json.loads(raw_data)['all_hotels']

    return {'tickets': tickets, 'hotels': hotels}

@celery_app.task(time_limit = task_timeout)
def transfer_task(data):
    try:
        taxi = get_transfers(data = data, budget = data['budget'])
    except:
        taxi = {{'transfer_to_hotel': None, 'transfer_to_origin': None}}
        logger.warning('taxi not found')
    return taxi

