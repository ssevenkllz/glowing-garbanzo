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
    """
    Parse time strings robustly. Handles:
    - '11:00 AM', '9:00 PM'
    - '5:00' (no AM/PM — assume PM if hour < 12, treat as PM)
    - 'Open 24 hours'
    Returns minutes since midnight (int) or None on failure.
    """
    t = t.strip()
    if not t:
        return None

    # Try with AM/PM
    for fmt in ("%I:%M %p", "%I %p"):
        try:
            dt = datetime.strptime(t, fmt)
            return dt.hour * 60 + dt.minute
        except:
            pass

    # Try without AM/PM (e.g. "5:00") — assume PM for hours < 8
    match = re.match(r'^(\d+):(\d+)$', t)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if hour < 8:
            hour += 12  # treat as PM
        return hour * 60 + minute

    return None

def parse_hours_entry(entry):
    """
    Parse a single hours string like:
    'Monday: 11:00 AM – 9:00 PM'
    'Thursday: 5:00 – 9:00 PM'
    'Monday: Open 24 hours'
    'Monday: Closed'
    Returns (open_mins, close_mins) or None if closed/unparseable.
    Special case: 24hr returns (0, 1440)
    """
    if "closed" in entry.lower():
        return None
    if "24 hours" in entry.lower() or "open 24" in entry.lower():
        return (0, 1440)

    # Strip day prefix
    colon_idx = entry.find(":")
    if colon_idx == -1:
        return None
    time_part = entry[colon_idx + 1:].strip()

    # Split on dash variants
    parts = re.split(r'\s*[–—-]\s*', time_part)
    if len(parts) != 2:
        return None

    open_str, close_str = parts[0].strip(), parts[1].strip()

    # If close has AM/PM but open doesn't, infer AM/PM for open
    close_has_ampm = bool(re.search(r'[AP]M', close_str, re.IGNORECASE))
    open_has_ampm = bool(re.search(r'[AP]M', open_str, re.IGNORECASE))

    if close_has_ampm and not open_has_ampm:
        # e.g. "5:00 – 9:00 PM" — open is same period as close unless close is AM
        close_period = "PM" if "PM" in close_str.upper() else "AM"
        # If open hour > close hour (e.g. open=5, close=9 PM), open is PM too
        open_match = re.match(r'(\d+)', open_str)
        if open_match:
            open_hour = int(open_match.group(1))
            open_str = f"{open_str} {close_period}"

    open_mins = parse_time_str(open_str)
    close_mins = parse_time_str(close_str)

    if open_mins is None or close_mins is None:
        return None

    return (open_mins, close_mins)

def minutes_now(dt):
    return dt.hour * 60 + dt.minute

def is_open_now(hours, user_dt):
    """Check if place is open at given datetime."""
    if not hours:
        return False

    day_name = DAY_MAP[user_dt.weekday()]
    current = minutes_now(user_dt)

    for entry in hours:
        if not entry.startswith(day_name):
            continue
        parsed = parse_hours_entry(entry)
        if parsed is None:
            return False  # closed today
        open_m, close_m = parsed
        if open_m == 0 and close_m == 1440:
            return True  # 24 hours
        # Handle overnight (e.g. 10 PM - 2 AM = 1320 - 120)
        if close_m < open_m:
            return current >= open_m or current <= close_m
        return open_m <= current <= close_m

    return False  # day not found = assume closed

def is_late_night(hours):
    """Check if place is open past 10 PM (1320 mins) on any day."""
    if not hours:
        return False
    for entry in hours:
        if "24 hours" in entry.lower():
            return True
        parsed = parse_hours_entry(entry)
        if parsed is None:
            continue
        open_m, close_m = parsed
        # overnight counts as late night
        if close_m < open_m:
            return True
        if close_m >= 1320:  # 10 PM
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
    timestamp = body.get("timestamp")
    utc_offset = body.get("utc_offset", 0)  # minutes offset from frontend

    if not choice:
        return jsonify({"error": "missing choice"}), 400

    query_filter = {"category": choice, "locale": locale}
    all_results = list(collection.find(query_filter, {"_id": 0}))

    # Parse user timestamp with UTC offset applied
    user_dt = None
    if timestamp:
        try:
            user_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            # Apply local offset (utc_offset is in minutes, negative for US timezones)
            from datetime import timedelta
            user_dt = user_dt + timedelta(minutes=utc_offset)
        except Exception as e:
            print(f"Timestamp parse error: {e}")

    # Filter: open now
    if open_now and user_dt:
        all_results = [r for r in all_results if is_open_now(r.get("hours", []), user_dt)]

    # Filter: late night
    if late_night:
        all_results = [r for r in all_results if is_late_night(r.get("hours", []))]

    # Sort by proximity
    if lat and lon:
        def proximity(r):
            coords = r.get("location", {}).get("coordinates", [None, None])
            if not coords or coords[0] is None:
                return float('inf')
            return ((coords[0] - lon) ** 2 + (coords[1] - lat) ** 2) ** 0.5
        all_results.sort(key=proximity)

    results = all_results[:10]

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


@app.route("/debug-time", methods=["POST"])
def debug_time():
    body = request.get_json()
    timestamp = body.get("timestamp")
    utc_offset = body.get("utc_offset", 0)
    
    from datetime import timedelta
    user_dt = None
    if timestamp:
        try:
            user_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            user_dt_local = user_dt + timedelta(minutes=utc_offset)
            return jsonify({
                "timestamp_received": timestamp,
                "utc_offset_received": utc_offset,
                "utc_time": str(user_dt),
                "local_time_computed": str(user_dt_local),
                "hour": user_dt_local.hour,
                "minute": user_dt_local.minute,
                "weekday": user_dt_local.weekday(),
                "day_name": DAY_MAP[user_dt_local.weekday()]
            })
        except Exception as e:
            return jsonify({"error": str(e)})
    return jsonify({"error": "no timestamp"})
