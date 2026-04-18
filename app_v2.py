from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["sample_restaurants"]
collection = db["restaurants"]

CUISINE_MAP = {
    "eat": ["American", "Italian", "Chinese", "Mexican", "Japanese", "Indian", "Pizza"],
    "drink": ["Café/Coffee/Tea", "Juice, Smoothies, Fruit Salads", "Delicatessen"],
    "play": ["Ice Cream, Gelato, Yogurt, Ices", "Bakery", "Donuts"],
}

@app.route("/query", methods=["POST"])
def query():
    body = request.get_json()
    choice = body.get("choice")
    lat = body.get("lat")
    lon = body.get("lon")

    if not choice:
        return jsonify({"error": "missing choice"}), 400

    cuisines = CUISINE_MAP.get(choice, [])
    query_filter = {"cuisine": {"$in": cuisines}}

    if lat and lon:
        pipeline = [
            {"$match": query_filter},
            {"$addFields": {
                "distance": {
                    "$sqrt": {
                        "$add": [
                            {"$pow": [{"$subtract": [{"$arrayElemAt": ["$address.coord", 0]}, lon]}, 2]},
                            {"$pow": [{"$subtract": [{"$arrayElemAt": ["$address.coord", 1]}, lat]}, 2]}
                        ]
                    }
                }
            }},
            {"$sort": {"distance": 1}},
            {"$limit": 10},
            {"$project": {"_id": 0, "name": 1, "cuisine": 1, "borough": 1, "address": 1, "distance": 1}}
        ]
        results = list(collection.aggregate(pipeline))
    else:
        results = list(collection.find(
            query_filter,
            {"_id": 0, "name": 1, "cuisine": 1, "borough": 1, "address": 1}
        ).limit(10))

    return jsonify({"choice": choice, "location": {"lat": lat, "lon": lon} if lat else None, "count": len(results), "results": results})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
