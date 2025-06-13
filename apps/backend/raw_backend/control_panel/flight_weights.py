from itertools import combinations

import pandas as pd


def weights_for_flight_tickets(activity_tag, trip_duration, budget_tag):
    if budget_tag == 'Budget':                           #and activity_tag  = 'summer_vacation' and trip_duration >10:
        weights = {'price score': 5,
                   'stay on location score': 2,
                   'total flight duration score': 1,
                   'number of segments score': 2
                   }
    elif budget_tag == 'Standard':                       #and activity_tag  = 'summer_vacation' and trip_duration >10:
        weights = {'price score': 2,
                   'stay on location score': 3,
                   'total flight duration score': 3,
                   'number of segments score': 2
                   }
    elif budget_tag == 'Lux':                        #and budget_tag == 'standard' and trip_duration > 5:
        weights = {'price score': 2,
                   'stay on location score': 3,
                   'total flight duration score': 15,
                   'number of segments score': 20
                   }
    else:
        weights = {'price score': 5,                 #and activity_tag  = 'summer_vacation' and trip_duration >10:
                   'stay on location score': 0,
                   'total flight duration score': 5,
                   'number of segments score': 0
                   }
    return weights

