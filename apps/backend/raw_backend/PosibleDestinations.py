
from backend.raw_backend.support.support_function_updated import connected_destinations, all_destinations, insert_distances
from backend.raw_backend.support.support_objects import main_database, skiing_database




class Destinations:

    def __init__(self, user_input):

        super().__init__()

        if user_input.destination == "":
            self.destinations = {
                'amadeus_direct': {},
                'flight_edge': connected_destinations(user_input.departure_location, user_input.departure_date, user_input.return_date, one_stop_allowed=user_input.one_stop_allowed)
            }
        else:
            self.destinations = user_input.destination

        self.all_destination = all_destinations(self.destinations)

        self.df = insert_distances(data=main_database,
                                   origin_coor=user_input.departure_location_coordinates,
                                   list_of_airports=self.all_destination
                                   ).sort_values(by=['city population'], ascending=False)
        print('sve destinacije',len(self.df))
        self.df.insert(loc=0, column='origin airport', value=user_input.departure_location)
        self.df.insert(loc=1, column='trip duration', value=user_input.trip_duration.days)


        self.ski_resorts = insert_distances(data=skiing_database,
                                            origin_coor=user_input.departure_location_coordinates,
                                            list_of_airports=self.all_destination
                                      )
        self.ski_resorts.insert(loc=0, column='origin airport', value=user_input.departure_location)
        self.ski_resorts.insert(loc=1, column='trip duration', value=user_input.trip_duration.days)



















