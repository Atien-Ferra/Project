"""
Reward definitions.
"""

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
