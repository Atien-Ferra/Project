"""
Rewards service for Focus Flow.
Handles reward definitions, checking, and awarding.
"""
from datetime import datetime, timezone
from bson.objectid import ObjectId
from db import get_db

# Define available rewards
REWARD_DEFINITIONS = [
    {
        "id": "first_task",
        "name": "First Step",
        "description": "Complete your first task",
        "icon": "🎯",
        "points": 10,
        "tier": "bronze",
        "condition": {"type": "tasks_done", "threshold": 1}
    },
    {
        "id": "task_master_5",
        "name": "Getting Started",
        "description": "Complete 5 tasks",
        "icon": "⭐",
        "points": 25,
        "tier": "bronze",
        "condition": {"type": "tasks_done", "threshold": 5}
    },
    {
        "id": "task_master_10",
        "name": "Task Master",
        "description": "Complete 10 tasks",
        "icon": "🌟",
        "points": 50,
        "tier": "silver",
        "condition": {"type": "tasks_done", "threshold": 10}
    },
    {
        "id": "task_master_25",
        "name": "Productivity Pro",
        "description": "Complete 25 tasks",
        "icon": "💫",
        "points": 100,
        "tier": "silver",
        "condition": {"type": "tasks_done", "threshold": 25}
    },
    {
        "id": "task_master_50",
        "name": "Task Champion",
        "description": "Complete 50 tasks",
        "icon": "🏆",
        "points": 200,
        "tier": "gold",
        "condition": {"type": "tasks_done", "threshold": 50}
    },
    {
        "id": "task_master_100",
        "name": "Legendary Achiever",
        "description": "Complete 100 tasks",
        "icon": "👑",
        "points": 500,
        "tier": "gold",
        "condition": {"type": "tasks_done", "threshold": 100}
    },
    {
        "id": "streak_3",
        "name": "On Fire",
        "description": "Maintain a 3-day streak",
        "icon": "🔥",
        "points": 30,
        "tier": "bronze",
        "condition": {"type": "streak", "threshold": 3}
    },
    {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon": "🔥🔥",
        "points": 75,
        "tier": "silver",
        "condition": {"type": "streak", "threshold": 7}
    },
    {
        "id": "streak_14",
        "name": "Unstoppable",
        "description": "Maintain a 14-day streak",
        "icon": "🔥🔥🔥",
        "points": 150,
        "tier": "silver",
        "condition": {"type": "streak", "threshold": 14}
    },
    {
        "id": "streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day streak",
        "icon": "🌋",
        "points": 300,
        "tier": "gold",
        "condition": {"type": "streak", "threshold": 30}
    },
    {
        "id": "quiz_first",
        "name": "Quiz Taker",
        "description": "Complete your first quiz",
        "icon": "📝",
        "points": 15,
        "tier": "bronze",
        "condition": {"type": "quizzes_taken", "threshold": 1}
    },
    {
        "id": "quiz_5",
        "name": "Knowledge Seeker",
        "description": "Complete 5 quizzes",
        "icon": "📚",
        "points": 50,
        "tier": "bronze",
        "condition": {"type": "quizzes_taken", "threshold": 5}
    },
    {
        "id": "quiz_10",
        "name": "Quiz Enthusiast",
        "description": "Complete 10 quizzes",
        "icon": "🎓",
        "points": 100,
        "tier": "silver",
        "condition": {"type": "quizzes_taken", "threshold": 10}
    },
    {
        "id": "quiz_25",
        "name": "Scholar",
        "description": "Complete 25 quizzes",
        "icon": "🏅",
        "points": 250,
        "tier": "gold",
        "condition": {"type": "quizzes_taken", "threshold": 25}
    },
]


def get_user_rewards(user_id: str) -> list:
    """
    Get all rewards earned by a user.
    """
    db = get_db()
    rewards_collection = db["rewards"]
    
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return []
    
    rewards = list(rewards_collection.find({"user_id": user_oid}))
    
    # Enrich with reward details
    result = []
    for r in rewards:
        reward_def = next((rd for rd in REWARD_DEFINITIONS if rd["id"] == r.get("reward_id")), None)
        if reward_def:
            result.append({
                "_id": str(r["_id"]),
                "reward_id": r.get("reward_id"),
                "name": reward_def["name"],
                "description": reward_def["description"],
                "icon": reward_def["icon"],
                "points": reward_def["points"],
                "tier": reward_def["tier"],
                "earned_at": r.get("earned_at")
            })
    
    return result


def get_total_points(user_id: str) -> int:
    """
    Calculate total points earned by a user.
    """
    rewards = get_user_rewards(user_id)
    return sum(r.get("points", 0) for r in rewards)


def check_and_award_rewards(user_id: str) -> list:
    """
    Check if user qualifies for any new rewards and award them.
    Returns list of newly awarded rewards.
    """
    db = get_db()
    users_collection = db["users"]
    rewards_collection = db["rewards"]
    
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return []
    
    # Get user stats
    user = users_collection.find_one({"_id": user_oid})
    if not user:
        return []
    
    tasks_done = user.get("tasks_done", 0)
    streak = user.get("streak", 0)
    quizzes_taken = user.get("quizzes_taken", 0)
    
    # Get already earned reward IDs
    earned_rewards = set(
        r["reward_id"] for r in rewards_collection.find(
            {"user_id": user_oid},
            {"reward_id": 1}
        )
    )
    
    new_rewards = []
    
    for reward_def in REWARD_DEFINITIONS:
        reward_id = reward_def["id"]
        
        # Skip if already earned
        if reward_id in earned_rewards:
            continue
        
        condition = reward_def["condition"]
        condition_type = condition["type"]
        threshold = condition["threshold"]
        
        # Check if condition is met
        qualified = False
        if condition_type == "tasks_done" and tasks_done >= threshold:
            qualified = True
        elif condition_type == "streak" and streak >= threshold:
            qualified = True
        elif condition_type == "quizzes_taken" and quizzes_taken >= threshold:
            qualified = True
        
        if qualified:
            # Award the reward
            reward_doc = {
                "user_id": user_oid,
                "reward_id": reward_id,
                "earned_at": datetime.now(timezone.utc)
            }
            rewards_collection.insert_one(reward_doc)
            
            new_rewards.append({
                "reward_id": reward_id,
                "name": reward_def["name"],
                "description": reward_def["description"],
                "icon": reward_def["icon"],
                "points": reward_def["points"],
                "tier": reward_def["tier"]
            })
    
    return new_rewards


def get_available_rewards() -> list:
    """
    Get all available reward definitions.
    """
    return REWARD_DEFINITIONS.copy()


def get_user_progress(user_id: str) -> dict:
    """
    Get user's progress towards all rewards.
    """
    db = get_db()
    users_collection = db["users"]
    rewards_collection = db["rewards"]
    
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        return {}
    
    user = users_collection.find_one({"_id": user_oid})
    if not user:
        return {}
    
    tasks_done = user.get("tasks_done", 0)
    streak = user.get("streak", 0)
    quizzes_taken = user.get("quizzes_taken", 0)
    
    earned_rewards = set(
        r["reward_id"] for r in rewards_collection.find(
            {"user_id": user_oid},
            {"reward_id": 1}
        )
    )
    
    progress = []
    for reward_def in REWARD_DEFINITIONS:
        condition = reward_def["condition"]
        condition_type = condition["type"]
        threshold = condition["threshold"]
        
        if condition_type == "tasks_done":
            current = tasks_done
        elif condition_type == "streak":
            current = streak
        elif condition_type == "quizzes_taken":
            current = quizzes_taken
        else:
            current = 0
        
        progress.append({
            "reward_id": reward_def["id"],
            "name": reward_def["name"],
            "description": reward_def["description"],
            "icon": reward_def["icon"],
            "points": reward_def["points"],
            "tier": reward_def["tier"],
            "current": current,
            "threshold": threshold,
            "earned": reward_def["id"] in earned_rewards,
            "progress_percent": min(100, int((current / threshold) * 100)) if threshold > 0 else 100
        })
    
    return {
        "rewards": progress,
        "total_points": get_total_points(user_id),
        "stats": {
            "tasks_done": tasks_done,
            "streak": streak,
            "quizzes_taken": quizzes_taken
        }
    }
