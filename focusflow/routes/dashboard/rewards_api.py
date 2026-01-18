"""
Rewards API endpoints.
"""
from flask import jsonify
from flask_login import login_required, current_user
from ...services.rewards import get_user_rewards, get_total_points, check_and_award_rewards
from . import dashboard_bp


@dashboard_bp.route("/api/rewards", methods=["GET"])
@login_required
def get_rewards():
    """Get all rewards earned by the current user."""
    rewards = get_user_rewards(current_user.id)
    total_points = get_total_points(current_user.id)
    
    return jsonify({
        "success": True,
        "rewards": rewards,
        "total_points": total_points
    }), 200


@dashboard_bp.route("/api/rewards/check", methods=["POST"])
@login_required
def check_rewards():
    """Check and award any new rewards the user has earned."""
    new_rewards = check_and_award_rewards(current_user.id)
    
    return jsonify({
        "success": True,
        "new_rewards": new_rewards
    }), 200
