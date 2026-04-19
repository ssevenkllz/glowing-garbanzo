import os
import time
import requests
from pymongo import MongoClient

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

# Singapore CBD / Marina Bay / Raffles Place
# Per Zero Corp policy Tier 1 hotels — Marriott, Hilton, Hyatt
# Closest cluster: Marina Bay Sands area, Raffles Hotel area
SGP_LAT = 1.2838
SGP_LON = 103.8591
SEARCH_RADIUS = 3000  # ~2 miles — CBD, Marina Bay, Raffles, Chinatown

SEARCH_TERMS = [
    "restaurant Singapore CBD Marina Bay",
    "bar Singapore Clarke Quay",
    "cafe Singapore CBD",
    "rooftop bar Singapore Marina Bay",
    "hawker centre Singapore CBD",
    "cocktail bar Singapore",
]

client = MongoClient(MONGO_URI)
db = client["wdywd"]
collection = db["places"]

seen_ids = set()

def search_places(query, lat, lon, radius):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join([
            "places.id", "places.displayName", "places.formattedAddress",
            "places.location", "places.nationalPhoneNumber",
            "places.regularOpeningHours", "places.delivery",
            "places.takeout", "places.dineIn", "places.primaryType",
            "places.types", "places.rating", "places.userRatingCount",
        ])
    }
    body = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lon},
                "radius": radius
            }
        },
        "maxResultCount": 20
    }
    res = requests.post(url, headers=headers, json=body)
    res.raise_for_status()
    return res.json().get("places", [])

def map_category(types):
    drink_types = {"bar", "night_club", "brewery", "cafe", "coffee_shop", "wine_bar", "cocktail_bar"}
    play_types = {"bowling_alley", "amusement_park", "movie_theater", "casino", "comedy_club", "tourist_attraction", "night_club"}
    types_set = set(types)
    if types_set & drink_types:
        return "drink"
    elif types_set & play_types:
        return "play"
    else:
        return "eat"

def ingest():
    inserted = 0
    skipped = 0
    for term in SEARCH_TERMS:
        print(f"Searching: {term}...")
        try:
            places = search_places(term, SGP_LAT, SGP_LON, SEARCH_RADIUS)
        except Exception as e:
            print(f"  Error: {e}")
            continue
        for place in places:
            place_id = place.get("id")
            if not place_id or place_id in seen_ids:
                skipped += 1
                continue
            seen_ids.add(place_id)
            hours = place.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
            doc = {
                "place_id": place_id,
                "name": place.get("displayName", {}).get("text", ""),
                "address": place.get("formattedAddress", ""),
                "location": {
                    "type": "Point",
                    "coordinates": [
                        place.get("location", {}).get("longitude"),
                        place.get("location", {}).get("latitude"),
                    ]
                },
                "phone": place.get("nationalPhoneNumber", ""),
                "hours": hours,
                "delivery": place.get("delivery", False),
                "takeout": place.get("takeout", False),
                "dine_in": place.get("dineIn", False),
                "types": place.get("types", []),
                "category": map_category(place.get("types", [])),
                "rating": place.get("rating"),
                "rating_count": place.get("userRatingCount"),
                "city": "Singapore",
                "state": "Singapore",
                "locale": "SGP",
            }
            collection.update_one({"place_id": place_id}, {"$set": doc}, upsert=True)
            inserted += 1
            print(f"  + {doc['name']} [{doc['category']}]")
        time.sleep(0.5)
    print(f"\nDone! {inserted} places inserted/updated, {skipped} duplicates skipped.")

if __name__ == "__main__":
    ingest()
