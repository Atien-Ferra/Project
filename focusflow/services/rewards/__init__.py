"""
Rewards service module.
Handles reward definitions, checking, and awarding.
"""
from .definitions import REWARD_DEFINITIONS
from .handlers import (
    get_user_rewards,
    get_total_points,
    check_and_award_rewards,
    get_available_rewards,
    get_user_progress
)

__all__ = [
    'REWARD_DEFINITIONS',
    'get_user_rewards',
    'get_total_points',
    'check_and_award_rewards',
    'get_available_rewards',
    'get_user_progress'
]
