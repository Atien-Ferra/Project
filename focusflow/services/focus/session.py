"""
Focus Session Logic
====================
This module handles focus session modes and recording completed study sessions.
"""
from datetime import datetime
from bson.objectid import ObjectId
from db import get_db
from ..streaks.handlers import record_streak_event, calculate_current_streak

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


def record_focus_session(user_id, mode, duration_minutes, completed=True, task_id=None):
    """
    Records a focus session in the database and updates user stats.
    
    Args:
        user_id: The ID of the user who completed the session
        mode: The mode used (pomodoro, short_break, etc.)
        duration_minutes: How many minutes they studied
        completed: Whether the session was finished to the end
        task_id: Optional ID of a task that was completed during this session
    """
    db = get_db()
    sessions = db["focus_sessions"]
    users = db["users"]
    tasks = db["tasks"]
    
    session_data = {
        "user_id": ObjectId(user_id),
        "mode": mode,
        "duration_minutes": duration_minutes,
        "completed": completed,
        "timestamp": datetime.now()
    }
    
    if task_id:
        session_data["task_id"] = ObjectId(task_id)
    
    result = sessions.insert_one(session_data)
    
    # If completed a focus session (not a break), increment stats
    if completed and mode == "pomodoro":
        # Record streak event first
        record_streak_event("focus_session", {"session_id": str(result.inserted_id)})
        
        # Calculate updated streak to persist
        streak = calculate_current_streak(user_id)
        
        update_query = {
            "$inc": {"focus_points": 5},
            "$set": {"streak": streak}
        }
        
        # If a task was linked, we need to handle its credit
        can_increment_tasks_done = True
        if task_id:
            try:
                task_oid = ObjectId(task_id)
                task = tasks.find_one({"_id": task_oid})
                
                if task:
                    # Mark task as done in any case
                    tasks.update_one({"_id": task_oid}, {"$set": {"done": True}})
                    
                    # But ONLY increment tasks_done if the task hasn't been credited yet
                    if task.get("stats_credited"):
                        can_increment_tasks_done = False
                    else:
                        tasks.update_one({"_id": task_oid}, {"$set": {"stats_credited": True}})
            except:
                pass

        if can_increment_tasks_done:
            update_query["$inc"]["tasks_done"] = 1
            
        users.update_one({"_id": ObjectId(user_id)}, update_query)
        
    return str(result.inserted_id)
