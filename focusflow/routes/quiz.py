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
import logging

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/dashboard", methods=["GET", "POST"])
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

    # IMPORTANT: exclude dismissed
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

    # Fetch tasks...
    user_tasks = list(tasks_collection.find(
        {"user_id": ObjectId(current_user.id)}
    ).sort("created_at", -1))
    for task in user_tasks:
        task["_id"] = str(task["_id"])  # Convert ObjectId to string for JSON serialization

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if not file or file.filename == "":
            flash("No file selected", "error")
            return redirect(url_for("quiz.dashboard"))

        if not allowed_file(file.filename):
            flash("Invalid file type. Upload PDF, DOCX, TXT, or images.", "error")
            return redirect(url_for("quiz.dashboard"))

        filename = secure_filename(file.filename)
        file_type = filename.rsplit(".", 1)[1].lower()
        temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(temp_path)

        extracted = extract_text_from_file(temp_path, file_type)
        if not extracted or not extracted.strip():
            try: os.remove(temp_path)
            except: pass
            flash("Could not read the file (empty/unreadable).", "error")
            return redirect(url_for("quiz.dashboard"))

        questions = generate_questions_from_text_lmstudio(extracted, num_questions=5)
        if not questions:
            try: os.remove(temp_path)
            except: pass
            flash("Could not generate questions. Upload a document with more content.", "error")
            return redirect(url_for("quiz.dashboard"))

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
        notifications=user_notifications
    )

@quiz_bp.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = (request.form.get("task_title") or "").strip()
    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("quiz.dashboard"))

    db = get_db()
    tasks_collection = db["tasks"]

    result = tasks_collection.insert_one({
        "user_id": ObjectId(current_user.id),
        "title": title,
        "done": False,
        "created_at": datetime.now(),
    })

    # Create a notification that a new task needs to be done
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
    return redirect(url_for("quiz.dashboard"))


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
        return redirect(url_for("quiz.dashboard"))

    if request.method == "POST":
        score = 0
        for idx, q in enumerate(current_questions):
            user_answer = request.form.get(f"q{idx+1}")
            if user_answer == q.get("correct_answer"):
                score += 1

        total = len(current_questions)
        percentage = int((score / total) * 100) if total else 0
        passed = percentage >= 60

        # delete uploaded file
        try:
            cf = user_doc.get("current_file") or {}
            fp = cf.get("file_path")
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass

        update = {"$inc": {"quizzes_taken": 1}, "$unset": {"current_questions": "", "current_file": ""}}
        if passed:
            update["$inc"]["streak"] = 1
            update["$inc"]["tasks_done"] = 1

        users.update_one({"_id": ObjectId(current_user.id)}, update)

        return jsonify({"score": score, "total": total, "percentage": percentage, "passed": passed})

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

        # prevent changing email to one that already exists
        exists = users.find_one({"email": email, "_id": {"$ne": ObjectId(current_user.id)}})
        if exists:
            flash("That email is already in use.", "error")
            return redirect(url_for("quiz.profile"))

        users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"name": name, "email": email}},
        )

        # keep Flask-Login user object in sync for the current request/session
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


@quiz_bp.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    """Get all tasks for the current user."""
    db = get_db()
    tasks_collection = db["tasks"]

    # Fetch tasks for the current user
    tasks = list(tasks_collection.find(
        {"user_id": ObjectId(current_user.id)}
    ).sort("created_at", -1))

    # Convert ObjectId and datetime fields to strings for JSON serialization
    for task in tasks:
        task["_id"] = str(task["_id"])
        task["user_id"] = str(task["user_id"])
        task["created_at"] = task["created_at"].isoformat()

    return jsonify({"success": True, "tasks": tasks}), 200


@quiz_bp.route("/api/tasks", methods=["POST"])
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


@quiz_bp.route("/api/tasks/<task_id>", methods=["DELETE"])
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


@quiz_bp.route("/api/tasks/<task_id>/toggle", methods=["PATCH"])
@login_required
def toggle_task(task_id):
    """Toggle the completion status of a task."""
    db = get_db()
    tasks_collection = db["tasks"]
    users_collection = db["users"]

    try:
        # Fetch the current task
        task = tasks_collection.find_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(current_user.id)
        })

        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404

        new_done_status = not task.get("done", False)

        # Update the task's done status
        result = tasks_collection.update_one(
            {"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)},
            {"$set": {"done": new_done_status}}
        )

        if result.modified_count > 0:
            # Create a notification reflecting the new status
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

            # Check if all tasks are completed
            all_tasks_done = tasks_collection.count_documents({
                "user_id": ObjectId(current_user.id),
                "done": False
            }) == 0

            if all_tasks_done:
                # Check if the streak has already been incremented today
                today = datetime.now().date()
                user = users_collection.find_one({"_id": ObjectId(current_user.id)})
                last_streak_update = user.get("last_streak_update")

                if not last_streak_update or last_streak_update.date() < today:
                    # Increment streak and update the last streak update date
                    users_collection.update_one(
                        {"_id": ObjectId(current_user.id)},
                        {
                            "$inc": {"streak": 1},
                            "$set": {"last_streak_update": datetime.now()}
                        }
                    )
            return jsonify({"success": True, "done": new_done_status}), 200
        else:
            return jsonify({"success": False, "error": "Failed to update task"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    

@quiz_bp.route("/api/notifications", methods=["GET"])
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


@quiz_bp.route("/api/notifications/dismiss/<notification_id>", methods=["PATCH"])
@login_required
def dismiss_notification(notification_id):
    db = get_db()
    notifications = db["notifications"]

    try:
        notif_oid = ObjectId(notification_id)
        user_oid = ObjectId(current_user.id)
    except Exception:
        # Always 200; indicate failure in JSON only
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
            # Not found or already dismissed
            return jsonify({
                "success": False,
                "error": "Not found or already dismissed"
            }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 200