"""
Notification API endpoints.
"""
from flask import jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from db import get_db
from . import dashboard_bp


@dashboard_bp.route("/api/notifications", methods=["GET"])
@login_required
def get_notifications():
    """Return active (non-dismissed) notifications for the current user."""
    try:
        db = get_db()
        notifications = db["notifications"]

        user_oid = ObjectId(current_user.id)

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
            # Safely convert payload, handling any ObjectIds
            payload = n.get("payload") or {}
            safe_payload = {}
            for key, value in payload.items():
                if isinstance(value, ObjectId):
                    safe_payload[key] = str(value)
                else:
                    safe_payload[key] = value
            
            result.append({
                "_id": str(n["_id"]),
                "type": n.get("type"),
                "status": n.get("status"),
                "payload": safe_payload,
            })

        return jsonify({"success": True, "notifications": result}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e), "notifications": []}), 200


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
