"""
Task API endpoints - CRUD operations for tasks.
"""
from datetime import datetime
from flask import request, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from db import get_db
from focusflow.services.notifications import create_notification
from ...services.streaks import record_streak_event, calculate_current_streak
from . import dashboard_bp


def serialize_value(value):
    """Convert MongoDB types to JSON-serializable types."""
    if isinstance(value, ObjectId):
        return str(value)
    elif hasattr(value, 'isoformat'):  # datetime objects
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    else:
        return value


def serialize_task(task):
    """Convert a task document to a JSON-serializable dict."""
    return {k: serialize_value(v) for k, v in task.items()}


@dashboard_bp.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    """Get all tasks for the current user."""
    try:
        db = get_db()
        tasks_collection = db["tasks"]

        # Find tasks for current user
        tasks = list(tasks_collection.find(
            {"user_id": ObjectId(current_user.id)}
        ))

        # Convert all tasks to JSON-serializable dicts
        result = [serialize_task(task) for task in tasks]

        # Sort by created_at descending
        result.sort(key=lambda x: x.get("created_at") or "", reverse=True)

        return jsonify({"success": True, "tasks": result}), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e), "tasks": []}), 200


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
