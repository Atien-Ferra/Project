"""
Focus Session Service
=====================
This module handles focus session logic, including session modes and
recording completed study sessions to improve user statistics.
"""

from datetime import datetime
from bson.objectid import ObjectId
from db import get_db

FOCUS_MODES = {
    "pomodoro": {
        "name": "Pomodoro",
        "duration": 25,  # minutes
        "description": "25 minutes of deep focus followed by a 5-minute break."
    },
    "short_break": {
        "name": "Short Break",
        "duration": 5,
        "description": "A quick 5-minute rest to recharge."
    },
    "long_break": {
        "name": "Long Break",
        "duration": 15,
        "description": "A longer 15-minute break after 4 focus sessions."
    }
}

def get_focus_modes():
    """Returns the available focus session modes."""
    return FOCUS_MODES

def record_focus_session(user_id, mode, duration_minutes, completed=True):
    """
    Records a focus session in the database.
    
    Args:
        user_id: The ID of the user who completed the session
        mode: The mode used (pomodoro, short_break, etc.)
        duration_minutes: How many minutes they studied
        completed: Whether the session was finished to the end
    """
    db = get_db()
    sessions = db["focus_sessions"]
    users = db["users"]
    
    session_data = {
        "user_id": ObjectId(user_id),
        "mode": mode,
        "duration_minutes": duration_minutes,
        "completed": completed,
        "timestamp": datetime.now()
    }
    
    result = sessions.insert_one(session_data)
    
    # If completed a focus session (not a break), potentially award points
    if completed and mode == "pomodoro":
        users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"focus_points": 5}}  # Small reward for focus
        )
        
    return str(result.inserted_id)
