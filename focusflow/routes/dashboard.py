"""
Dashboard and task-related routes.
Split from quiz.py for better organization.
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from db import get_db
from focusflow.services.notifications import create_notification
from ..services.files import allowed_file, extract_text_from_file
from ..services.questions import generate_questions_from_text_lmstudio
from ..services.streaks import record_streak_event, calculate_current_streak
from ..services.rewards import get_user_rewards, get_total_points, check_and_award_rewards

dashboard_bp = Blueprint("dashboard", __name__)


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

        questions = generate_questions_from_text_lmstudio(extracted, num_questions=5)
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


# ============== API ROUTES ==============

@dashboard_bp.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    """Get all tasks for the current user."""
    db = get_db()
    tasks_collection = db["tasks"]

    tasks = list(tasks_collection.find(
        {"user_id": ObjectId(current_user.id)}
    ).sort("created_at", -1))

    for task in tasks:
        task["_id"] = str(task["_id"])
        task["user_id"] = str(task["user_id"])
        task["created_at"] = task["created_at"].isoformat()

    return jsonify({"success": True, "tasks": tasks}), 200


@dashboard_bp.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    """Create a new task for the current user."""
    data = request.get_json()
    title = (data.get("title") or "").strip()

    if not title:
        return jsonify({"success": False, "error": "Task title is required"}), 400

    db = get_db()
    tasks_collection = db["tasks"]

    result = tasks_collection.insert_one({
        "user_id": ObjectId(current_user.id),
        "title": title,
        "done": False,
        "created_at": datetime.now(),
    })

    return jsonify({
        "success": True,
        "task_id": str(result.inserted_id),
        "title": title,
        "done": False
    }), 201


@dashboard_bp.route("/api/tasks/<task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    """Delete a task for the current user."""
    db = get_db()
    tasks_collection = db["tasks"]

    try:
        result = tasks_collection.delete_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(current_user.id)
        })

        if result.deleted_count > 0:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@dashboard_bp.route("/api/tasks/<task_id>/toggle", methods=["PATCH"])
@login_required
def toggle_task(task_id):
    """Toggle the completion status of a task."""
    db = get_db()
    tasks_collection = db["tasks"]
    users_collection = db["users"]

    try:
        user_oid = ObjectId(current_user.id)
        task_oid = ObjectId(task_id)
    except Exception as e:
        return jsonify({"success": False, "error": f"Invalid id: {e}"}), 400

    try:
        task = tasks_collection.find_one({
            "_id": task_oid,
            "user_id": user_oid
        })

        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404

        old_done_status = task.get("done", False)
        new_done_status = not old_done_status

        result = tasks_collection.update_one(
            {"_id": task_oid, "user_id": user_oid},
            {"$set": {"done": new_done_status}}
        )

        if result.modified_count <= 0:
            return jsonify({"success": False, "error": "Failed to update task"}), 500

        create_notification(
            db=db,
            user_id=current_user.id,
            notification_type="task_due",
            payload={
                "taskId": str(task["_id"]),
                "title": task.get("title", ""),
                "done": new_done_status,
            },
        )

        # Only record streak event when going from not done -> done
        # FIX: This is the ONLY place streak is incremented for tasks
        if not old_done_status and new_done_status:
            record_streak_event("task", {"taskId": str(task_oid)})
            # Also increment tasks_done counter
            users_collection.update_one(
                {"_id": user_oid},
                {"$inc": {"tasks_done": 1}}
            )

        # Recalculate streak from streakEvents
        streak = calculate_current_streak(current_user.id)

        # Persist on user document
        users_collection.update_one(
            {"_id": user_oid},
            {"$set": {"streak": streak}}
        )

        return jsonify({"success": True, "done": new_done_status, "streak": streak}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@dashboard_bp.route("/api/notifications", methods=["GET"])
@login_required
def get_notifications():
    """Return active (non-dismissed) notifications for the current user."""
    db = get_db()
    notifications = db["notifications"]

    try:
        user_oid = ObjectId(current_user.id)
    except Exception:
        return jsonify({"success": False, "error": "Invalid current user id"}), 400

    docs = list(
        notifications
        .find({
            "userId": user_oid,
            "status": {"$ne": "dismissed"},
        })
        .sort("sentAt", -1)
    )

    result = []
    for n in docs:
        result.append({
            "_id": str(n["_id"]),
            "type": n.get("type"),
            "status": n.get("status"),
            "payload": n.get("payload") or {},
        })

    return jsonify({"success": True, "notifications": result}), 200


@dashboard_bp.route("/api/notifications/dismiss/<notification_id>", methods=["PATCH"])
@login_required
def dismiss_notification(notification_id):
    db = get_db()
    notifications = db["notifications"]

    try:
        notif_oid = ObjectId(notification_id)
        user_oid = ObjectId(current_user.id)
    except Exception:
        return jsonify({
            "success": False,
            "error": "Invalid id"
        }), 200

    try:
        result = notifications.update_one(
            {
                "_id": notif_oid,
                "userId": user_oid,
                "status": {"$ne": "dismissed"},
            },
            {"$set": {"status": "dismissed"}}
        )

        if result.modified_count > 0:
            return jsonify({"success": True}), 200
        else:
            return jsonify({
                "success": False,
                "error": "Not found or already dismissed"
            }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 200


# ============== REWARDS API ROUTES ==============

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
