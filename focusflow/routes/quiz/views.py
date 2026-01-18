"""
Quiz views - quiz display and submission.
"""
import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from db import get_db
from ...services.rewards import check_and_award_rewards
from ...services.streaks import record_streak_event, calculate_current_streak
from . import quiz_bp


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
        details = []  # Store detailed results for each question
        
        for idx, q in enumerate(current_questions):
            user_answer_id = request.form.get(f"q{idx+1}")
            correct_answer_id = q.get("correct_answer")
            is_correct = user_answer_id == correct_answer_id
            
            if is_correct:
                score += 1
            
            # Find the text for user's answer and correct answer
            user_answer_text = "No answer selected"
            correct_answer_text = ""
            
            for ans in q.get("answers", []):
                if ans.get("id") == user_answer_id:
                    user_answer_text = ans.get("text", "")
                if ans.get("id") == correct_answer_id:
                    correct_answer_text = ans.get("text", "")
            
            details.append({
                "question": q.get("question_text", f"Question {idx + 1}"),
                "user_answer": user_answer_text,
                "correct_answer": correct_answer_text,
                "is_correct": is_correct
            })

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
        
        if passed:
            # Record streak event
            record_streak_event("quiz", {"score": score, "total": total})
            
            # Calculate updated streak
            streak = calculate_current_streak(current_user.id)
            update["$set"] = {"streak": streak}
            
            # Handle task credit if a task_id was linked during upload
            task_id = user_doc.get("current_file", {}).get("task_id")
            can_increment_tasks_done = True
            
            if task_id:
                try:
                    tasks_collection = db["tasks"]
                    task_oid = ObjectId(task_id) if isinstance(task_id, str) else task_id
                    task = tasks_collection.find_one({"_id": task_oid})
                    
                    if task:
                        # Mark task as done
                        tasks_collection.update_one({"_id": task_oid}, {"$set": {"done": True}})
                        
                        # Only increment if not already credited
                        if task.get("stats_credited"):
                            can_increment_tasks_done = False
                        else:
                            tasks_collection.update_one({"_id": task_oid}, {"$set": {"stats_credited": True}})
                except:
                    pass
            
            if can_increment_tasks_done:
                update["$inc"]["tasks_done"] = 1

        users.update_one({"_id": ObjectId(current_user.id)}, update)
        
        # Check for new rewards after quiz completion
        check_and_award_rewards(current_user.id)

        return jsonify({
            "score": score,
            "total": total,
            "percentage": percentage,
            "passed": passed,
            "details": details  # Include answer details for review
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
