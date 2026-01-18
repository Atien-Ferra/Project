"""
Quiz-related routes.
Split from the original quiz.py for better organization.
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from db import get_db
from ..services.rewards import check_and_award_rewards

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    db = get_db()
    users = db["users"]

    user_doc = users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    current_questions = user_doc.get("current_questions")
    if not current_questions:
        flash("No quiz generated yet. Upload a document first.", "error")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        score = 0
        for idx, q in enumerate(current_questions):
            user_answer = request.form.get(f"q{idx+1}")
            if user_answer == q.get("correct_answer"):
                score += 1

        total = len(current_questions)
        percentage = int((score / total) * 100) if total else 0
        passed = percentage >= 60

        # Delete uploaded file
        try:
            cf = user_doc.get("current_file") or {}
            fp = cf.get("file_path")
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass

        # Update user stats
        update = {
            "$inc": {"quizzes_taken": 1},
            "$unset": {"current_questions": "", "current_file": ""}
        }
        
        # Only increment tasks_done if passed (not streak - that's handled by streakEvents)
        if passed:
            update["$inc"]["tasks_done"] = 1

        users.update_one({"_id": ObjectId(current_user.id)}, update)
        
        # Check for new rewards after quiz completion
        check_and_award_rewards(current_user.id)

        return jsonify({
            "score": score,
            "total": total,
            "percentage": percentage,
            "passed": passed
        })

    return render_template("quiz.html", questions=current_questions)


@quiz_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    users = db["users"]

    user_doc = users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()

        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("quiz.profile"))

        exists = users.find_one({"email": email, "_id": {"$ne": ObjectId(current_user.id)}})
        if exists:
            flash("That email is already in use.", "error")
            return redirect(url_for("quiz.profile"))

        users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"name": name, "email": email}},
        )

        current_user.name = name
        current_user.email = email

        flash("Profile updated.", "success")
        return redirect(url_for("quiz.profile"))

    return render_template(
        "profile.html",
        user_name=user_doc.get("name", ""),
        user_email=user_doc.get("email", ""),
        streak=user_doc.get("streak", 0),
        quizzes_taken=user_doc.get("quizzes_taken", 0),
        tasks_done=user_doc.get("tasks_done", 0),
    )


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

