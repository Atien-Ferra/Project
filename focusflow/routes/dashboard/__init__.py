"""
Dashboard routes module.
Handles dashboard view, tasks, notifications, rewards, and focus sessions.
"""
from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)

# Import routes after blueprint is created to avoid circular imports
from .views import *
from .tasks_api import *
from .notifications_api import *
from .rewards_api import *
from .focus_api import *
