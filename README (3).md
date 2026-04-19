# Zero Corp Travel Copilot & Concierge

> Everything a business traveler needs — before, during, and after the trip — in one trusted Copilot.

**Live Demo:** [ssevenkllz.github.io/glowing-garbanzo/chat_v4.html](https://ssevenkllz.github.io/glowing-garbanzo/chat_v4.html)  
**Backend:** [glowing-garbanzo-gmb0.onrender.com/health](https://glowing-garbanzo-gmb0.onrender.com/health)
> ⚠️ Hosted on Render free tier. A UptimeRobot health monitor pings the service every 5 minutes to prevent cold starts. We originally intended to deploy on DigitalOcean (offered as a hackathon sponsor credit) but were unable to access the free credits in time and pivoted to Render in under an hour.

---

## What We Built

Two fully integrated modules running on a single stack:

### 1. AI Travel Copilot
A persona-aware AI assistant that answers enterprise travel policy questions in plain language, grounded entirely in a synthesized company handbook stored in MongoDB Atlas. Powered by Claude Sonnet via the Anthropic API with real-time streaming responses.

**Three personas. One app. Totally different experiences:**
- **Kelli Chen (VP)** — concise, executive-level answers
- **Maya Patel (Junior Associate)** — warm, step-by-step guidance for a first-time international traveler
- **David Okafor (SVP Approver)** — facts-first, one-click approval summaries

### 2. wdywd — Local Discovery Module
A location-aware "what do you want to do?" tool that lets travelers find real eat/drink/play venues near them — or near any destination they're planning ahead for. Filters for open now, late night hours, and proximity sorting. Real venue data ingested from Google Places API and stored in MongoDB Atlas.

---

## The Demo Money Moment

Maya just wrapped her last client session in London. Her boyfriend has arrived. She opens the Copilot and asks:

> *"Ok I'm done with work — what should we do tonight in London?"*

The Copilot hands off seamlessly to the wdywd Discover module. Enterprise travel assistant becomes local discovery tool. **One app. Two modes.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML/CSS/JS · GitHub Pages |
| Backend | Python · Flask · Gunicorn · Render |
| Database | MongoDB Atlas (`wdywd.places` + `wdywd.docs`) |
| AI Model | Anthropic Claude Sonnet (streaming) |
| Venue Data | Google Places API (New) |
| Geolocation | Browser Geolocation API + Google Places Geocoding |

---

## The Data

### Venue Data — `wdywd.places`
Real venue records ingested from Google Places API across 4 cities:

| Locale | City | Records |
|---|---|---|
| LFK | Lawrence, KS | ~77 |
| NYC | Manhattan, NY | ~92 |
| LON | London, UK | ~100+ |
| SGP | Singapore CBD | ~100+ |

Each record includes: name, address, coordinates, phone, hours, delivery/takeout/dine-in flags, rating, and locale tag.

**Ingest once. Serve unlimited queries. $0 ongoing Google API cost.**

### Policy Handbook — `wdywd.docs`
7 sections of synthesized enterprise travel policy (~4,800 words) stored in MongoDB Atlas and injected as context on every Copilot query.

**Grounded in real regulatory sources:**
- GSA Federal Travel Regulations (FTR)
- IRS Publication 463 (Travel, Gift & Car Expenses)
- GBTA (Global Business Travel Association) policy templates
- Fortune 500 published travel policies (Salesforce, Google, etc.)
- IATA international travel guidelines

---

## Architecture

```
GitHub Pages (Frontend)
    chat_v4.html
         │
         ▼
Render · Flask (Backend · app_v8.py)
    /query  →  venue search + filters
    /chat   →  streaming AI responses
    /geocode → destination name → lat/lon
         │
         ├──► MongoDB Atlas
         │       wdywd.places  (370+ venues)
         │       wdywd.docs    (7 handbook sections)
         │
         └──► Anthropic API
                Claude Sonnet · streaming
                handbook context injected per query
```

**Key architectural decisions:**
- **Context stuffing over RAG (MVP):** Full handbook (~5,000 tokens) injected per query. Well within Claude's context window, negligible cost, zero infrastructure overhead.
- **RAG-ready by design:** The `/chat` endpoint is fully swappable. Upgrading to vector embeddings = internal change only. Frontend never changes.
- **One ingest, many queries:** Google Places API hit once per city. 1,000 users = same API cost as 1 user.
- **Same infra, two modules:** wdywd and Copilot share one cluster, one backend, one deployment.

---

## File Structure

```
glowing-garbanzo/
├── app_v8.py              # Flask backend (streaming chat, query, geocode)
├── chat_v4.html           # Full Copilot + Discover UI (streaming)
├── index_v6.html          # Standalone wdywd app
├── requirements_v1.txt    # Python dependencies
├── ingest_LFK_v1.py       # Lawrence KS venue ingestion
├── ingest_NYC_v1.py       # Manhattan venue ingestion
├── ingest_LON_v1.py       # London venue ingestion
├── ingest_SGP_v1.py       # Singapore venue ingestion
├── ingest_docs_v1.py      # Handbook docs ingestion
├── user_stories_v1.md     # Full user story documentation
└── docs/
    ├── section1_planning.md
    ├── section2_booking.md
    ├── section3_approvals.md
    ├── section4_during.md
    ├── section5_issues.md
    ├── section6_posttrip.md
    └── section7_privacy.md
```

---

## Version History

| Version | What Changed |
|---|---|
| app_v1 | Flask skeleton, placeholder query |
| app_v2 | Real query against MongoDB sample_restaurants |
| app_v3 | Switched to real wdywd.places collection, locale filter |
| app_v4 | Added open now, late night, sort by radius filters |
| app_v5 | Fixed hours parsing (AM/PM inference, overnight, UTC offset) |
| app_v6 | Added /chat endpoint with Claude API + persona context |
| app_v7 | Added /geocode endpoint for Planning Ahead feature |
| app_v8 | Streaming responses via Server-Sent Events |
| index_v1 | Base form, raw JSON results |
| index_v2 | Results as clean table |
| index_v3 | Render backend URL, publicly shareable |
| index_v4 | Results as cards with hours, badges, phone |
| index_v5 | Open now, late night, sort by distance toggles |
| index_v6 | UTC offset for accurate local time parsing |
| chat_v1 | Full Copilot UI + Concierge tab (non-streaming) |
| chat_v2 | Planning ahead toggle, persistent suggestions, mobile optimization |
| chat_v3 | Real-time streaming responses, auto tab switch on wdywd mention |
| chat_v4 | Renamed Discover → Concierge, updated title to Zero Corp Travel Copilot & Concierge |

---

## Environment Variables

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB Atlas connection string |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude Sonnet |
| `GOOGLE_API_KEY` | Google Maps Platform API key (Places API New) |

---

## Running Locally

```bash
# Install dependencies
pip install flask flask-cors pymongo gunicorn requests

# Set environment variables
export MONGO_URI="your_atlas_connection_string"
export ANTHROPIC_API_KEY="your_anthropic_key"
export GOOGLE_API_KEY="your_google_key"

# Run ingest scripts (once per city)
python ingestion/ingest_LFK_v1.py
python ingestion/ingest_docs_v1.py

# Start server
python app_v8.py

# Serve frontend
python -m http.server 8080
# Open: http://localhost:8080/chat_v4.html
```

---

## Privacy

- Conversation history retained for session only — not persisted to database
- No GPS data stored — coordinates used for proximity sorting only
- No credit card or passport data collected or stored
- AI model does not train on user data
- All API communication over TLS

---

## Built At

**HackKU26** · University of Kansas · April 2026  
36-hour hackathon

**Built with:** Flask · MongoDB Atlas · Anthropic Claude · Google Places API · GitHub Pages · Render
