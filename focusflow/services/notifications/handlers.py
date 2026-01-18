"""
Notification handling functions.
"""
from datetime import datetime
from bson.objectid import ObjectId


def create_notification(db, user_id, notification_type, payload):
    """Create a new notification."""
    notifications = db["notifications"]
    notification = {
        "userId": ObjectId(user_id),
        "type": notification_type,
        "scheduledFor": None,          # you can set a real datetime later
        "sentAt": datetime.now(),
        "status": "sent",              # or "scheduled" if you treat it differently
        "payload": payload,
    }
    notifications.insert_one(notification)
