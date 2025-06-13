



#gruba obrada activity tagova

class Tags:

    def __init__(self, distance_filter, activity_tag):
        super().__init__()
        self.activity_tag = activity_tag
        self.tag = distance_filter
        self.drop_cities_without_price = False
