"""
User profile route with study preferences.
"""
from datetime import datetime, timezone
from flask import render_template, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from db import get_db
from . import auth_bp


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile page with study preferences."""
    db = get_db()
    profiles_collection = db["profiles"]
    users_collection = db["users"]

    if request.method == "POST":
        try:
            session_length_mins = int(request.form.get("studyPrefs.sessionLengthMins", 0))
            break_long_mins = int(request.form.get("studyPrefs.breakLongMins", 0))
            preferred_difficulty = request.form.get("studyPrefs.preferredDifficulty")
            updated_at = datetime.now(timezone.utc)

            profiles_collection.update_one(
                {"user_id": ObjectId(current_user.id)},
                {
                    "$set": {
                        "studyPrefs.sessionLengthMins": session_length_mins,
                        "studyPrefs.breakLongMins": break_long_mins,
                        "studyPrefs.preferredDifficulty": preferred_difficulty,
                        "updatedAt": updated_at,
                    }
                },
            )
            return {"message": "Preferences updated successfully."}, 200
        except Exception as e:
            return {"error": str(e)}, 400

    user_data = users_collection.find_one({"_id": ObjectId(current_user.id)})
    profile_data = profiles_collection.find_one({"user_id": ObjectId(current_user.id)})

    if not profile_data:
        now = datetime.now(timezone.utc)
        profile_data = {
            "user_id": ObjectId(current_user.id),
            "displayName": current_user.name,
            "studyPrefs": {
                "sessionLengthMins": 25,
                "breakLongMins": 15,
                "preferredDifficulty": "medium",
            },
            "createdAt": now,
            "updatedAt": now,
        }
        profiles_collection.insert_one(profile_data)

    profile_data.update({
        "email": user_data.get("email"),
        "tasks_done": user_data.get("tasks_done", 0),
        "quizzes_taken": user_data.get("quizzes_taken", 0),
        "streak": user_data.get("streak", 0),
    })

    return render_template("profile.html", profile=profile_data)
