"""
Streaks service module.
Handles streak recording and calculation.
"""
from .handlers import record_streak_event, calculate_current_streak

__all__ = ['record_streak_event', 'calculate_current_streak']
