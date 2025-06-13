from backend.raw_backend.control_panel.trip_duration import trip_duration_OD, trip_duration_AP
import logging

logger = logging.getLogger('django')

class DistanceFilter:
    def __init__(self, possible_destinations, user_input):
        super().__init__()

        logger.info("DistanceFilter initialized")
        # logger.info(user_input)

        df = possible_destinations.df
        # logger.info("df")
        # logger.info(df)
        self.distance_filtered = df[
            (df['distance from origin'] < trip_duration_OD[user_input.trip_duration.days]) &
            (df['distance from airport'] < trip_duration_AP[user_input.trip_duration.days])
        ]
