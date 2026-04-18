from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import re
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["wdywd"]
collection = db["places"]

DAY_MAP = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
}

def parse_time_str(t):
    """Convert '10:00 PM' or '2:00 AM' to 24hr int like 2200 or 200."""
    t = t.strip()
    try:
        dt = datetime.strptime(t, "%I:%M %p")
        return dt.hour * 100 + dt.minute
    except:
        return None

def is_open_now(hours, user_dt):
    """Check if place is open at given datetime based on hours list."""
    day_name = DAY_MAP[user_dt.weekday()]
    current_time = user_dt.hour * 100 + user_dt.minute

    for entry in hours:
        if not entry.startswith(day_name):
            continue
        # e.g. "Monday: 7:00 AM – 10:00 PM"
        match = re.search(r'(\d+:\d+ [AP]M)\s*[–-]\s*(\d+:\d+ [AP]M)', entry)
        if not match:
            continue
        open_t = parse_time_str(match.group(1))
        close_t = parse_time_str(match.group(2))
        if open_t is None or close_t is None:
            continue
        # Handle overnight (e.g. 10 PM - 2 AM)
        if close_t < open_t:
            if current_time >= open_t or current_time <= close_t:
                return True
        else:
            if open_t <= current_time <= close_t:
                return True
    return False

def is_late_night(hours):
    """Check if place is open past 10 PM on any day."""
    for entry in hours:
        match = re.search(r'(\d+:\d+ [AP]M)\s*[–-]\s*(\d+:\d+ [AP]M)', entry)
        if not match:
            continue
        close_t = parse_time_str(match.group(2))
        if close_t is None:
            continue
        # Past 10 PM = 2200, or wraps overnight (close_t < open_t)
        open_t = parse_time_str(match.group(1))
        if close_t >= 2200 or (open_t and close_t < open_t):
            return True
    return False


@app.route("/query", methods=["POST"])
def query():
    body = request.get_json()
    choice = body.get("choice")
    lat = body.get("lat")
    lon = body.get("lon")
    locale = body.get("locale", "LFK")
    open_now = body.get("open_now", False)
    late_night = body.get("late_night", False)
    sort_by_radius = body.get("sort_by_radius", False)
    timestamp = body.get("timestamp")  # ISO string from frontend

    if not choice:
        return jsonify({"error": "missing choice"}), 400

    query_filter = {"category": choice, "locale": locale}

    # Pull all matching docs for Python-side filtering
    all_results = list(collection.find(query_filter, {"_id": 0}))

    # Parse user timestamp for open now check
    user_dt = None
    if timestamp:
        try:
            user_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except:
            pass

    # Filter: open now
    if open_now and user_dt:
        all_results = [r for r in all_results if r.get("hours") and is_open_now(r["hours"], user_dt)]

    # Filter: late night
    if late_night:
        all_results = [r for r in all_results if r.get("hours") and is_late_night(r["hours"])]

    # Sort by proximity if we have coords
    if lat and lon and (sort_by_radius or (lat and lon)):
        def proximity(r):
            coords = r.get("location", {}).get("coordinates", [None, None])
            if coords[0] is None or coords[1] is None:
                return float('inf')
            return ((coords[0] - lon) ** 2 + (coords[1] - lat) ** 2) ** 0.5
        all_results.sort(key=proximity)

    results = all_results[:10]

    # Clean up location field for response
    for r in results:
        r.pop("location", None)
        r.pop("place_id", None)
        r.pop("types", None)

    return jsonify({
        "choice": choice,
        "locale": locale,
        "location": {"lat": lat, "lon": lon} if lat else None,
        "filters": {"open_now": open_now, "late_night": late_night, "sort_by_radius": sort_by_radius},
        "count": len(results),
        "results": results,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
