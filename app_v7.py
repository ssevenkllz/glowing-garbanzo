from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import re
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = MongoClient(MONGO_URI)
db = client["wdywd"]
places_collection = db["places"]
docs_collection = db["docs"]

# ── existing wdywd helpers ──────────────────────────────────────────────────

DAY_MAP = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
}

def parse_time_str(t):
    t = t.strip()
    if not t:
        return None
    for fmt in ("%I:%M %p", "%I %p"):
        try:
            dt = datetime.strptime(t, fmt)
            return dt.hour * 60 + dt.minute
        except:
            pass
    match = re.match(r'^(\d+):(\d+)$', t)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if hour < 8:
            hour += 12
        return hour * 60 + minute
    return None

def parse_hours_entry(entry):
    if "closed" in entry.lower():
        return None
    if "24 hours" in entry.lower() or "open 24" in entry.lower():
        return (0, 1440)
    colon_idx = entry.find(":")
    if colon_idx == -1:
        return None
    time_part = entry[colon_idx + 1:].strip()
    parts = re.split(r'\s*[–—-]\s*', time_part)
    if len(parts) != 2:
        return None
    open_str, close_str = parts[0].strip(), parts[1].strip()
    close_has_ampm = bool(re.search(r'[AP]M', close_str, re.IGNORECASE))
    open_has_ampm = bool(re.search(r'[AP]M', open_str, re.IGNORECASE))
    if close_has_ampm and not open_has_ampm:
        close_period = "PM" if "PM" in close_str.upper() else "AM"
        open_str = f"{open_str} {close_period}"
    open_mins = parse_time_str(open_str)
    close_mins = parse_time_str(close_str)
    if open_mins is None or close_mins is None:
        return None
    return (open_mins, close_mins)

def is_open_now(hours, user_dt):
    if not hours:
        return False
    day_name = DAY_MAP[user_dt.weekday()]
    current = user_dt.hour * 60 + user_dt.minute
    for entry in hours:
        if not entry.startswith(day_name):
            continue
        parsed = parse_hours_entry(entry)
        if parsed is None:
            return False
        open_m, close_m = parsed
        if open_m == 0 and close_m == 1440:
            return True
        if close_m < open_m:
            return current >= open_m or current <= close_m
        return open_m <= current <= close_m
    return False

def is_late_night(hours):
    if not hours:
        return False
    for entry in hours:
        if "24 hours" in entry.lower():
            return True
        parsed = parse_hours_entry(entry)
        if parsed is None:
            continue
        open_m, close_m = parsed
        if close_m < open_m:
            return True
        if close_m >= 1320:
            return True
    return False

# ── wdywd query endpoint ────────────────────────────────────────────────────

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
    utc_offset = body.get("utc_offset", 0)

    if not choice:
        return jsonify({"error": "missing choice"}), 400

    query_filter = {"category": choice, "locale": locale}
    all_results = list(places_collection.find(query_filter, {"_id": 0}))

    user_dt = None
    if timestamp:
        try:
            from datetime import timedelta
            user_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            user_dt = user_dt + timedelta(minutes=utc_offset)
        except Exception as e:
            print(f"Timestamp parse error: {e}")

    if open_now and user_dt:
        all_results = [r for r in all_results if is_open_now(r.get("hours", []), user_dt)]
    if late_night:
        all_results = [r for r in all_results if is_late_night(r.get("hours", []))]
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

# ── copilot chat endpoint ───────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    import urllib.request
    import json as pyjson

    body = request.get_json()
    user_message = body.get("message", "").strip()
    history = body.get("history", [])  # list of {role, content} dicts
    persona = body.get("persona", "kelli")  # kelli | maya | david

    if not user_message:
        return jsonify({"error": "missing message"}), 400

    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "missing ANTHROPIC_API_KEY"}), 500

    # Pull all handbook docs from Atlas
    docs = list(docs_collection.find({}, {"_id": 0, "content": 1, "title": 1, "section": 1}))
    handbook_text = "\n\n---\n\n".join(
        f"## Section {d['section']}: {d['title']}\n\n{d['content']}"
        for d in sorted(docs, key=lambda x: x["section"])
    )

    # Persona context
    persona_context = {
        "kelli": "The user is Kelli Chen, VP of Client Partnerships at Zero Corp. She is an experienced traveler who knows the system but wants the Copilot to handle the details. She is busy and prefers concise, actionable responses.",
        "maya": "The user is Maya Patel, a Junior Associate and direct report to Kelli Chen. This is her first international trip under Zero Corp policy. She is anxious and needs warm, plain-language guidance. Walk her through things step by step when needed.",
        "david": "The user is David Okafor, SVP of Operations and Kelli's approver. He is busy and wants clean, concise summaries. He does not want to ask follow-up questions. Give him the facts upfront.",
    }.get(persona, "The user is a Zero Corp employee.")

    system_prompt = f"""You are the Zero Corp Travel Copilot — a helpful, friendly, and knowledgeable AI assistant for Zero Corp business travelers.

{persona_context}

Your job is to answer questions about Zero Corp's travel policy, help with trip planning, approvals, in-trip issues, and post-trip reimbursement.

You answer ONLY from the Zero Corp Travel & Expense Policy Handbook provided below. If the answer is not in the handbook, say so clearly and direct the user to the Travel Desk at travel@zerocorp.com or (800) 555-0192.

Be concise. Use bullet points for action items. Lead with the most important information. For urgent or safety situations, lead with the emergency contact first.

When the user asks about things to do, eat, drink, or play in a city for personal time — warmly acknowledge the shift to personal time and let them know the wdywd feature can help with local recommendations. Say something like: "Sounds like you're off the clock! The wdywd module can help you find great spots nearby — just head to the Discover tab and pick eat, drink, or play."

--- ZERO CORP TRAVEL & EXPENSE POLICY HANDBOOK ---

{handbook_text}

--- END OF HANDBOOK ---

Always be helpful, warm, and human. You are reducing traveler stress, not adding to it."""

    # Build messages array with history
    messages = []
    for h in history[-10:]:  # keep last 10 turns for context
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

    # Call Anthropic API
    payload = pyjson.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = pyjson.loads(resp.read().decode("utf-8"))
            reply = result["content"][0]["text"]
            return jsonify({"reply": reply})
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"Anthropic API error: {e.code} — {error_body}")
        return jsonify({"error": f"API error {e.code}", "detail": error_body}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

# ── health ──────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/debug-time", methods=["POST"])
def debug_time():
    from datetime import timedelta
    body = request.get_json()
    timestamp = body.get("timestamp")
    utc_offset = body.get("utc_offset", 0)
    if timestamp:
        try:
            user_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            user_dt_local = user_dt + timedelta(minutes=utc_offset)
            return jsonify({
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)


@app.route("/geocode", methods=["POST"])
def geocode():
    """Convert a destination name to lat/lon + locale using Google Places."""
    import urllib.request as ureq
    import json as pyjson

    body = request.get_json()
    query = body.get("query", "").strip()
    if not query:
        return jsonify({"error": "missing query"}), 400

    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        return jsonify({"error": "missing GOOGLE_API_KEY"}), 500

    url = "https://places.googleapis.com/v1/places:searchText"
    headers_dict = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.location,places.formattedAddress",
    }
    payload = pyjson.dumps({
        "textQuery": query,
        "maxResultCount": 1,
    }).encode("utf-8")

    req = ureq.Request(url, data=payload, headers=headers_dict, method="POST")
    try:
        with ureq.urlopen(req) as resp:
            data = pyjson.loads(resp.read().decode("utf-8"))
            places = data.get("places", [])
            if not places:
                return jsonify({"error": "not found"}), 404
            place = places[0]
            lat = place["location"]["latitude"]
            lon = place["location"]["longitude"]
            label = place.get("displayName", {}).get("text", query)
            address = place.get("formattedAddress", "")

            # Detect locale from address
            locale = "LFK"
            addr_lower = address.lower()
            if "new york" in addr_lower or "manhattan" in addr_lower or "brooklyn" in addr_lower:
                locale = "NYC"
            elif "london" in addr_lower or "england" in addr_lower:
                locale = "LON"
            elif "singapore" in addr_lower:
                locale = "SGP"
            elif "kansas city" in addr_lower or "missouri" in addr_lower:
                locale = "LFK"  # close enough for now

            return jsonify({"lat": lat, "lon": lon, "label": label, "address": address, "locale": locale})
    except Exception as e:
        print(f"Geocode error: {e}")
        return jsonify({"error": str(e)}), 500
