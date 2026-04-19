import os
import glob
from datetime import datetime
from pymongo import MongoClient

# --- Config ---
MONGO_URI = os.environ.get("MONGO_URI")

# --- DB setup ---
client = MongoClient(MONGO_URI)
db = client["wdywd"]
collection = db["docs"]

# Section metadata — maps filename to human-readable info
SECTION_META = {
    "section1_planning.md": {
        "section": 1,
        "title": "Travel Planning & Preparation",
        "topics": ["planning", "preparation", "booking windows", "preferred vendors",
                   "international travel", "risk assessment", "checklist", "passport", "visa"]
    },
    "section2_booking.md": {
        "section": 2,
        "title": "Booking Policy",
        "topics": ["booking", "airfare", "flights", "class of service", "business class",
                   "economy", "hotel", "car rental", "rideshare", "mileage", "refundable",
                   "non-refundable", "concur", "preferred vendors"]
    },
    "section3_approvals.md": {
        "section": 3,
        "title": "Approvals",
        "topics": ["approval", "approvals", "authorization", "manager approval", "VP approval",
                   "approval chain", "how to approve", "denied", "rejection", "emergency travel",
                   "submit approval", "concur"]
    },
    "section4_during.md": {
        "section": 4,
        "title": "During Travel",
        "topics": ["covered", "not covered", "meals", "per diem", "incidentals",
                   "flight delay", "cancellation", "rebooking", "lost luggage",
                   "medical emergency", "emergency contacts", "travel desk", "reimbursable"]
    },
    "section5_issues.md": {
        "section": 5,
        "title": "Issues & Exceptions",
        "topics": ["issues", "disruption", "exception", "out of policy", "medical emergency",
                   "security incident", "escalation", "who to contact", "emergency",
                   "something went wrong", "help"]
    },
    "section6_posttrip.md": {
        "section": 6,
        "title": "Post-Trip & Reimbursement",
        "topics": ["expense report", "reimbursement", "receipts", "deadline", "submit expenses",
                   "concur", "rejection", "hotel folio", "after the trip", "close out",
                   "what do I still need to do"]
    },
    "section7_privacy.md": {
        "section": 7,
        "title": "Privacy & Data",
        "topics": ["privacy", "data", "what is collected", "stored", "protected",
                   "third party", "sharing", "security", "GDPR", "employee rights"]
    },
}

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")


def ingest():
    inserted = 0
    updated = 0

    md_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))

    if not md_files:
        print(f"No markdown files found in {DOCS_DIR}")
        return

    for filepath in sorted(md_files):
        filename = os.path.basename(filepath)
        meta = SECTION_META.get(filename)

        if not meta:
            print(f"  Skipping {filename} — no metadata defined")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        doc = {
            "doc_id": filename.replace(".md", ""),
            "filename": filename,
            "section": meta["section"],
            "title": meta["title"],
            "topics": meta["topics"],
            "content": content,
            "word_count": len(content.split()),
            "source": "Zero Corp Travel & Expense Policy Handbook v1",
            "last_updated": datetime.utcnow().isoformat(),
            "locale": "global",
        }

        result = collection.update_one(
            {"doc_id": doc["doc_id"]},
            {"$set": doc},
            upsert=True
        )

        if result.upserted_id:
            inserted += 1
            print(f"  + Inserted: Section {meta['section']} — {meta['title']} ({doc['word_count']} words)")
        else:
            updated += 1
            print(f"  ~ Updated:  Section {meta['section']} — {meta['title']} ({doc['word_count']} words)")

    print(f"\nDone! {inserted} docs inserted, {updated} docs updated in wdywd.docs")
    print(f"Total docs in collection: {collection.count_documents({})}")


if __name__ == "__main__":
    ingest()
