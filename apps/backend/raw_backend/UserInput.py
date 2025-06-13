import json
import logging
from datetime import datetime
from .support.support_functions import one_stop, time_object
from .support.support_objects import airport_coordinates

logger = logging.getLogger('django')


class UserInput():
    def __init__(self, data):
        super().__init__()

        if isinstance(data, dict):
            self.data = data
            # If data is a JSON string, convert it to a dictionary
        elif isinstance(data, str):
            self.data = json.loads(data)
        else:
            raise ValueError("Invalid data format. Expected dict or JSON string.")

        print("self.data type", type(self.data))

        # ovo treba da bude lista aerodrom da bi dobili vise potencijalnih lokacija,
        # medjutim neophodno je da imamo koordinate korisnika,
        # to mozemo da dobijemo iskljucivo kroz mobilnu aplikaciju

        self.departure_location = str(self.data.get('departureLocation'))
        self.destination = str(self.data.get('destination'))
        self.adults = int(self.data.get('adults'))
        self.children = int(self.data.get('children'))
        self.departure_date = str(self.data.get('departureDate'))
        self.return_date = str(self.data.get('returnDate'))
        self.exclude_llc = True

        if self.destination == '':
            self.picked_destination = False
        else:
            self.picked_destination = True

        logger.info("return date RADE", self.return_date)
        self.trip_duration = time_object(self.return_date) - time_object(self.departure_date)
        self.one_stop_allowed = one_stop(days=self.trip_duration.days)
        self.departure_location_coordinates = (airport_coordinates.loc[self.departure_location, 0],
                                               airport_coordinates.loc[self.departure_location, 1])






