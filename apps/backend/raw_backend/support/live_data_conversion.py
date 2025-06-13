import json
import os

def update_offer_data(data_directory, offer_id):
    print("Update offer data")
    file_path = os.path.join(data_directory, f'offerData{offer_id}.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON")
        return None

    if not data or len(data) < 5:
        print("Error: Insufficient data entries")
        return data

    return data
    # if not live_flight_data:
    #     print("Error: No live flight data provided")
    #     return data
    #
    # if not live_flight_data.get("oneWay"):
    #     if "price" not in live_flight_data or "currency" not in live_flight_data["price"] or "total" not in live_flight_data["price"]:
    #         print("Error: Missing price information in live flight data")
    #         return data
    #
    #     currency = currency_converter(live_flight_data["price"]["currency"])
    #     new_price = live_flight_data["price"]["total"]
    #
    #     if "itineraries" not in live_flight_data or len(live_flight_data["itineraries"]) < 2:
    #         print("Error: Expected exactly two itineraries")
    #         return data
    #
    #     total_duration_first = live_flight_data["itineraries"][0].get("duration")
    #     total_duration_return = live_flight_data["itineraries"][1].get("duration")
    #
    #     first_offer = data[0]
    #     return_offer = data[4]
    #
    #     update_offer_details(first_offer, live_flight_data["itineraries"][0], new_price, currency, total_duration_first)
    #     update_offer_details(return_offer, live_flight_data["itineraries"][1], new_price, currency, total_duration_return)
    #
    #     return data
    # else:
    #     print("Here comes code for two separate flights")
    #     return data


def update_offer_details(offer, itinerary, new_price, currency, total_duration):
    if not offer or not itinerary:
        print("Error: Missing offer or itinerary data")
        return {}

    offer.setdefault("info1", {}).setdefault("selection-box", {}).setdefault("option1", {})
    offer["info1"]["selection-box"]["option1"]["price"] = f"{new_price}{currency}"
    offer["info1"].setdefault("details", [{}])
    offer["info1"]["details"][0]["totalDuration"] = f"{total_duration}"

    if "segments" not in offer["info1"]["details"][0]:
        offer["info1"]["details"][0]["segments"] = []

    segments = offer["info1"]["details"][0]["segments"]
    itinerary_segments = itinerary.get("segments", [])

    for index, segment_data in enumerate(itinerary_segments):
        print(f"Processing segment {index}: {segment_data}")  # Debug print
        if index >= len(segments):
            segments.append({})
        segment_info = segments[index]
        update_segment(segment_info, segment_data)

    if len(segments) > len(itinerary_segments):
        segments[:] = segments[:len(itinerary_segments)]


def update_segment(segment_info, segment_data):
    if not segment_info or not segment_data:
        print("Error: Missing segment information")
        return {}

    print(f"Updating segment with data: {segment_data}")  # Debug print

    segment_info["departure"] = {
        "iataCode": segment_data["departure"].get("iataCode", ""),
        "terminal": segment_data["departure"].get("terminal", ""),
        "at": segment_data["departure"].get("at", "")
    }
    segment_info["arrival"] = {
        "iataCode": segment_data["arrival"].get("iataCode", ""),
        "terminal": segment_data["arrival"].get("terminal", ""),
        "at": segment_data["arrival"].get("at", "")
    }
    segment_info["duration"] = segment_data.get("duration", "")
    segment_info["carrier"] = segment_data.get("carrierCode", "")
    segment_info["aircraft"] = segment_data.get("aircraft", {}).get("code", "")
    segment_info["flightNumber"] = segment_data.get("number", "")
    segment_info["numberOfStops"] = segment_data.get("numberOfStops", 0)


def currency_converter(currency):
    return "€" if currency.upper() == "EUR" else currency