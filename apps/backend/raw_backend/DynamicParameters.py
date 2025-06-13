from backend.raw_backend.support.support_functions import flights_offers, compute_difference
from backend.raw_backend.control_panel.flight_segments_allowed import destinations_search


class DynamicParameters:
    def __init__(self, top_scored, user_input):
        super().__init__()

        top_airports = []
        for j in range(len(top_scored.top_scored[0])):
            for index in top_scored[0][j].keys():
                top_airports.append(top_scored[0][j][index]['destination airport'])
        self.top_airports = list(set(top_airports))

        max_destinations = min(destinations_search, len(top_airports))

        self.flight = flights_offers(list_of_destinations=top_airports[:max_destinations],
                                     adults=user_input.adults,
                                     children=user_input.children,
                                     departure=user_input.departure_date,
                                     return_date=user_input.return_date,
                                     origin=user_input.departure_location,
                                     non_stop=user_input.one_stop_allowed)

        self.list_of_new_airports = compute_difference(top_airports, top_airports[:max_destinations])


        if len(self.flight[1])<max_destinations:
            try:
                self.second_round = flights_offers(list_of_destinations=self.list_of_new_airports[:min(len(self.list_of_new_airports), (max_destinations-len(self.flight[1])))],
                                                     adults=user_input.adults,
                                                     children=user_input.children,
                                                     departure=user_input.departure_date,
                                                     return_date=user_input.return_date,
                                                     origin=user_input.departure_location,
                                                     non_stop=user_input.one_stop_allowed)
                self.all_flights = self.flight[0] + self.second_round[0]
            except:
                self.all_flights = self.flight[0]


        else:
            self.all_flights = self.flight[0]

    def get_data(self, data):
        self.data = data