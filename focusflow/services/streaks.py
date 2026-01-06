from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_login import current_user
from db import get_db

def record_streak_event(source: str, meta: dict | None = None):
    """
    Record a streak event for the current user for 'today' and given source,
    but only if it doesn't already exist for that (user, date, source).
    """
    db = get_db()
    streak_events = db["streakEvents"]

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        user_oid = ObjectId(current_user.id)
    except Exception:
        return

    existing = streak_events.find_one({
        "userId": user_oid,
        "date": today,
        "source": source,
    })

    if existing:
        return

    doc = {
        "userId": user_oid,
        "date": today,
        "source": source,
    }
    if meta:
        doc["meta"] = meta

    streak_events.insert_one(doc)

def calculate_current_streak(user_id: str) -> int:
    db = get_db()
    streak_events = db["streakEvents"]

    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return 0

    # Get all distinct event dates as strings
    date_strings = streak_events.distinct("date", {"userId": user_oid})
    if not date_strings:
        return 0

    # Convert to date objects
    dates = sorted(
        [datetime.strptime(d, "%Y-%m-%d").date() for d in date_strings],
        reverse=True  # newest first
    )

    today = datetime.now().date()

    # Shortcut: if the latest event is older than yesterday, streak is 0
    if dates[0] < today - timedelta(days=1):
        return 0

    # Build a set for quick membership tests
    date_set = set(dates)

    streak = 0
    current_day = today

    # Walk backwards one day at a time while we find events
    while current_day in date_set:
        streak += 1
        current_day = current_day - timedelta(days=1)

    return streak