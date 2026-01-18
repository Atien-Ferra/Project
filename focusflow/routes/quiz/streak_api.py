"""
Streak API endpoint.
"""
from flask import jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from db import get_db
from . import quiz_bp


@quiz_bp.route("/api/increment-streak", methods=["POST"])
@login_required
def increment_streak():
    """Increment the current user's streak and return the updated value."""
    db = get_db()
    users = db["users"]
    
    user = users.find_one({"_id": ObjectId(current_user.id)})
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    # Increment the streak by 1
    result = users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$inc": {"streak": 1}}
    )
    
    if result.modified_count > 0:
        # Get the updated user document to return the new streak value
        updated_user = users.find_one({"_id": ObjectId(current_user.id)})
        return jsonify({
            "success": True,
            "streak": updated_user.get("streak", 0)
        }), 200
    else:
        return jsonify({"success": False, "error": "Failed to update streak"}), 500
