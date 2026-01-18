"""
User class and loader for Flask-Login.
"""
from flask_login import UserMixin
from bson.objectid import ObjectId
from db import get_db
from ...extensions import login_manager


class User(UserMixin):
    """User class for Flask-Login."""
    def __init__(self, user_id: str, name: str, email: str):
        self.id = user_id
        self.name = name
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    """Load user from database."""
    db = get_db()
    doc = db["users"].find_one({"_id": ObjectId(user_id)})
    if not doc:
        return None
    return User(str(doc["_id"]), doc.get("name", ""), doc.get("email", ""))
