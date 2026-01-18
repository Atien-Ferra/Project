"""
Quiz routes module.
Handles quiz display, submission, and streak management.
"""
from flask import Blueprint

quiz_bp = Blueprint("quiz", __name__)

# Import routes after blueprint is created to avoid circular imports
from .views import *
from .streak_api import *
