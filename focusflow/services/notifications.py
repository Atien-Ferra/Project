from datetime import datetime
from bson.objectid import ObjectId

def create_notification(db, user_id, notification_type, payload):
    """Create a new notification."""
    notifications = db["notifications"]
    notification = {
        "userId": ObjectId(user_id),
        "type": notification_type,
        "sentAt": datetime.now(),
        "status": "scheduled",
        "payload": payload,
    }
    notifications.insert_one(notification)
