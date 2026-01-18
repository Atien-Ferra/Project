"""
Main dashboard view and form-based task add.
"""
import os
import random
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from db import get_db
from focusflow.services.notifications import create_notification
from ...services.files import allowed_file, extract_text_from_file
from ...services.questions import generate_questions_from_text_lmstudio
from ...services.rewards import get_user_rewards, get_total_points
from . import dashboard_bp


@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    db = get_db()
    users = db["users"]
    notifications = db["notifications"]
    tasks_collection = db["tasks"]

    user_doc = users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    # Exclude dismissed notifications
    user_notifications = list(
        notifications
        .find({
            "userId": ObjectId(current_user.id),
            "status": {"$ne": "dismissed"},
        })
        .sort("sentAt", -1)
    )
    for notification in user_notifications:
        notification["_id"] = str(notification["_id"])

    # Fetch tasks
    user_tasks = list(tasks_collection.find(
        {"user_id": ObjectId(current_user.id)}
    ).sort("created_at", -1))
    for task in user_tasks:
        task["_id"] = str(task["_id"])

    # Get user rewards
    user_rewards = get_user_rewards(current_user.id)
    total_points = get_total_points(current_user.id)

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if not file or file.filename == "":
            flash("No file selected", "error")
            return redirect(url_for("dashboard.dashboard"))

        if not allowed_file(file.filename):
            flash("Invalid file type. Upload PDF, DOCX, TXT, or images.", "error")
            return redirect(url_for("dashboard.dashboard"))

        filename = secure_filename(file.filename)
        file_type = filename.rsplit(".", 1)[1].lower()
        temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(temp_path)

        extracted = extract_text_from_file(temp_path, file_type)
        if not extracted or not extracted.strip():
            try:
                os.remove(temp_path)
            except:
                pass
            flash("Could not read the file (empty/unreadable).", "error")
            return redirect(url_for("dashboard.dashboard"))

        # Calculate dynamic number of questions based on text length
        # Base of 5 questions, +1 for every 1000 chars, max 15
        # Also add a bit of randomness as requested
        text_len = len(extracted)
        target_count = min(max(5, (text_len // 1000) + random.randint(0, 2)), 15)
        
        questions = generate_questions_from_text_lmstudio(extracted, num_questions=target_count)
        if not questions:
            try:
                os.remove(temp_path)
            except:
                pass
            flash("Could not generate questions. Upload a document with more content.", "error")
            return redirect(url_for("dashboard.dashboard"))

        users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "current_file": {
                    "filename": filename,
                    "file_path": temp_path,
                    "file_type": file_type,
                    "uploaded_at": datetime.now(),
                },
                "current_questions": questions
            }}
        )

        flash("File uploaded successfully! Quiz generated.", "success")
        return redirect(url_for("quiz.quiz"))

    return render_template(
        "dashboard.html",
        user_name=current_user.name,
        streak=user_doc.get("streak", 0),
        quizzes_taken=user_doc.get("quizzes_taken", 0),
        tasks_done=user_doc.get("tasks_done", 0),
        tasks=user_tasks,
        notifications=user_notifications,
        rewards=user_rewards,
        total_points=total_points
    )


@dashboard_bp.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = (request.form.get("task_title") or "").strip()
    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("dashboard.dashboard"))

    db = get_db()
    tasks_collection = db["tasks"]

    result = tasks_collection.insert_one({
        "user_id": ObjectId(current_user.id),
        "title": title,
        "done": False,
        "created_at": datetime.now(),
    })

    create_notification(
        db=db,
        user_id=current_user.id,
        notification_type="task_due",
        payload={
            "taskId": str(result.inserted_id),
            "title": title,
            "done": False,
        },
    )

    flash("Task added.", "success")
    return redirect(url_for("dashboard.dashboard"))
