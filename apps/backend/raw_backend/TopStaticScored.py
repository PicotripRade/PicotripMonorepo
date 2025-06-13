
from backend.raw_backend.control_panel.top_static_score import top_static_score_locations, \
    number_of_cities_per_country, number_of_cities_per_airport


class TopScored:
    def __init__(self, data, picked_destination):
        super().__init__()
        if picked_destination == ['all countries']:
            geo_filtered = data
        else:
            geo_filtered = data[data.loc[:, 'city country'].isin(picked_destination)]
        self.static_offer = geo_filtered.groupby('airport').head(number_of_cities_per_airport)
        self.static_offer = geo_filtered.groupby('city country').head(number_of_cities_per_country)
        self.static_offer = self.static_offer.iloc[:min(len(self.static_offer), top_static_score_locations)]

        self.cities = list(self.static_offer.loc[:, 'city'])
        self.coordinates = list(self.static_offer.loc[:, 'city coor'])[0:len(self.cities)]
        print(self.coordinates)









