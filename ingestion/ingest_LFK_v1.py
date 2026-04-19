import os
import time
import requests
from pymongo import MongoClient

# --- Config ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

# Lawrence, KS center point
LFK_LAT = 38.9717
LFK_LON = -95.2353
SEARCH_RADIUS = 8000  # meters (~5 miles)

# Search terms to cover eat/drink/play
SEARCH_TERMS = [
    "restaurant",
    "bar",
    "cafe",
    "coffee shop",
    "brewery",
    "bakery",
]

# --- DB setup ---
client = MongoClient(MONGO_URI)
db = client["wdywd"]
collection = db["places"]

# Avoid duplicates across search terms
seen_ids = set()


def search_places(query, lat, lon, radius):
    """Search Places API (New) for a given query and location."""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join([
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.nationalPhoneNumber",
            "places.regularOpeningHours",
            "places.delivery",
            "places.takeout",
            "places.dineIn",
            "places.primaryType",
            "places.types",
            "places.rating",
            "places.userRatingCount",
        ])
    }
    body = {
        "textQuery": f"{query} in Lawrence Kansas",
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
    """Map Google place types to our eat/drink/play categories."""
    drink_types = {"bar", "night_club", "brewery", "cafe", "coffee_shop", "wine_bar", "cocktail_bar"}
    play_types = {"bowling_alley", "amusement_park", "movie_theater", "casino", "comedy_club", "karaoke"}
    
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
            places = search_places(term, LFK_LAT, LFK_LON, SEARCH_RADIUS)
        except Exception as e:
            print(f"  Error: {e}")
            continue

        for place in places:
            place_id = place.get("id")
            if not place_id or place_id in seen_ids:
                skipped += 1
                continue
            seen_ids.add(place_id)

            # Parse hours
            hours_raw = place.get("regularOpeningHours", {})
            hours = hours_raw.get("weekdayDescriptions", [])

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
                "city": "Lawrence",
                "state": "KS",
                "locale": "LFK",
            }

            # Upsert so re-running doesn't duplicate
            collection.update_one(
                {"place_id": place_id},
                {"$set": doc},
                upsert=True
            )
            inserted += 1
            print(f"  + {doc['name']} [{doc['category']}]")

        time.sleep(0.5)  # be polite to the API

    print(f"\nDone! {inserted} places inserted/updated, {skipped} duplicates skipped.")


if __name__ == "__main__":
    ingest()
