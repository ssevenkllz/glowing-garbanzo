from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["wdywd"]
collection = db["places"]


@app.route("/query", methods=["POST"])
def query():
    body = request.get_json()
    choice = body.get("choice")      # eat / drink / play
    lat = body.get("lat")
    lon = body.get("lon")
    locale = body.get("locale", "LFK")  # default to LFK for now

    if not choice:
        return jsonify({"error": "missing choice"}), 400

    query_filter = {
        "category": choice,
        "locale": locale,
    }

    if lat and lon:
        pipeline = [
            {"$match": query_filter},
            {"$addFields": {
                "distance": {
                    "$sqrt": {
                        "$add": [
                            {"$pow": [{"$subtract": [{"$arrayElemAt": ["$location.coordinates", 0]}, lon]}, 2]},
                            {"$pow": [{"$subtract": [{"$arrayElemAt": ["$location.coordinates", 1]}, lat]}, 2]}
                        ]
                    }
                }
            }},
            {"$sort": {"distance": 1}},
            {"$limit": 10},
            {"$project": {
                "_id": 0,
                "name": 1,
                "address": 1,
                "phone": 1,
                "hours": 1,
                "delivery": 1,
                "takeout": 1,
                "dine_in": 1,
                "category": 1,
                "rating": 1,
                "distance": 1,
            }}
        ]
        results = list(collection.aggregate(pipeline))
    else:
        results = list(collection.find(
            query_filter,
            {"_id": 0, "name": 1, "address": 1, "phone": 1, "hours": 1,
             "delivery": 1, "takeout": 1, "dine_in": 1, "category": 1, "rating": 1}
        ).limit(10))

    return jsonify({
        "choice": choice,
        "locale": locale,
        "location": {"lat": lat, "lon": lon} if lat else None,
        "count": len(results),
        "results": results,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
