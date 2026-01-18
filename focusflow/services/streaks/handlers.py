"""
Streak recording and calculation functions.
"""
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_login import current_user
from db import get_db


def record_streak_event(source: str, meta: dict | None = None):
    """
    Records a milestone event (like completing a task or focus session).
    Events are deduplicated by user+date+source so multiple completions 
    on the same day only count as one streak contribution.
    """
    db = get_db()
    streak_events = db["streakEvents"]

    # Use YYYY-MM-DD string as the primary key for daily grouping
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        user_oid = ObjectId(current_user.id)
    except Exception:
        return

    # Check if this specific source already contributed to the streak today
    existing = streak_events.find_one({
        "userId": user_oid,
        "date": today,
        "source": source,
    })

    if existing:
        return # Already recorded for today

    doc = {
        "userId": user_oid,
        "date": today,
        "source": source,
    }
    if meta:
        doc["meta"] = meta

    # Insert the event into MongoDB
    streak_events.insert_one(doc)


def calculate_current_streak(user_id: str) -> int:
    """
    Calculates the current consecutive daily streak for a user.
    The streak continues as long as there is at least one event per day.
    A streak is broken if a day (yesterday or older) is skipped.
    """
    db = get_db()
    streak_events = db["streakEvents"]

    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return 0

    # Retrieve all unique dates the user was active
    date_strings = streak_events.distinct("date", {"userId": user_oid})
    if not date_strings:
        return 0

    # Parse strings into date objects and sort newest-first
    dates = sorted(
        [datetime.strptime(d, "%Y-%m-%d").date() for d in date_strings],
        reverse=True
    )

    today = datetime.now().date()

    # If the most recent activity was before yesterday, the streak is DEAD
    if dates[0] < today - timedelta(days=1):
        return 0

    # Convert sorted dates to a Set for O(1) lookups in the loop
    date_set = set(dates)

    streak = 0
    current_day = today

    # We start from 'today' and step backwards day-by-day.
    # If a day exists in the activity set, the streak continues.
    # Note: If today isn't in set but yesterday IS, streak starts from yesterday.
    
    # Check if user has done something TODAY
    if today not in date_set:
        current_day = today - timedelta(days=1)

    while current_day in date_set:
        streak += 1
        current_day = current_day - timedelta(days=1)

    return streak
