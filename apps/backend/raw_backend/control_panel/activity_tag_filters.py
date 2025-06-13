from backend.raw_backend.control_panel.activity_tag_raw_params import filter
from backend.raw_backend.support.support_function_updated import include_area, exclude_area


## FILTER PARAMS


def filter_countries(df, activity_tag,departure_data = 2024-11-10, return_date = 2024-11-21):
    filtered = df[df['city country'].isin(filter['countries'][activity_tag].keys())]
    return filtered


def filter_population(df, activity_tag,departure_data = 2024-11-10, return_date = 2024-11-21):

    filtered = df[
        (df['city population']<filter['population'][activity_tag]['max_population'])&
        (df['city population']>filter['population'][activity_tag]['min_population'])
    ]
    return filtered

def filter_geo_area(df, activity_tag, departure_data = 2024-11-10, return_date = 2024-11-21):
    filtered = include_area(df = df, min_max_coordinates_list=filter['geo_area'][activity_tag])
    return filtered


def filter_geo_area_exclude(df, activity_tag, departure_data = 2024-11-10, return_date = 2024-11-21):
    filtered = exclude_area(df = df, min_max_coordinates_list=filter['geo_area_exclude'][activity_tag])
    return filtered