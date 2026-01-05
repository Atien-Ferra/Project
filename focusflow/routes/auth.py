import os, secrets, hashlib
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..extensions import login_manager
from db import get_db

auth_bp = Blueprint("auth", __name__)
limiter = Limiter(get_remote_address)

PEPPER = os.getenv("PASSWORD_PEPPER")
if not PEPPER:
    raise RuntimeError("PASSWORD_PEPPER not set")


class User(UserMixin):
    def __init__(self, user_id: str, name: str, email: str):
        self.id = user_id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    doc = db["users"].find_one({"_id": ObjectId(user_id)})
    if not doc:
        return None
    return User(str(doc["_id"]), doc.get("name", ""), doc.get("email", ""))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        remember = bool(request.form.get("remember"))

        pepper = os.getenv("PASSWORD_PEPPER", "")
        password_to_check = password + pepper

        db = get_db()
        user_doc = db["users"].find_one({"email": email})

        if user_doc and check_password_hash(user_doc["password"], password_to_check):
            user = User(str(user_doc["_id"]), user_doc.get("name", ""), user_doc.get("email", ""))
            login_user(user, remember=remember)
            flash("Login successful!", "success")
            return redirect(url_for("quiz.dashboard"))

        flash("Invalid email or password", "error")

    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_with_pepper = password + PEPPER
        confirm_password = request.form.get("confirm_password")
        terms = request.form.get("terms")

        if not all([name, email, password, confirm_password]):
            flash("Please fill all required fields", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("signup.html")

        if not terms:
            flash("Please accept the terms and conditions", "error")
            return render_template("signup.html")

        db = get_db()
        users_collection = db["users"]

        if users_collection.find_one({"email": email}):
            flash("Email already registered", "error")
            return render_template("signup.html")

        hashed_pw = generate_password_hash(
            password_with_pepper,
            method="scrypt",      
            salt_length=16        
        )
        result = users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw,
            "streak": 0,
            "quizzes_taken": 0,
            "tasks_done": 0,
            "files": []
        })
        user = User(str(result.inserted_id), name, email)
        login_user(user)
        flash("Account created successfully!", "success")
        return redirect(url_for("quiz.dashboard"))

    return render_template("signup.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("main.index"))

@auth_bp.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    if request.method == "POST":
        flash("If the email exists, a reset link has been sent", "success")
        return redirect(url_for("auth.login"))
    return render_template("forgotpassword.html")


@auth_bp.route("/updatepassword/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    if request.method == "POST":
        new_password = request.form.get("new_password") or ""
        confirm = request.form.get("confirm_password") or ""

        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("resetpassword.html")

        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("resetpassword.html")

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc)

        db = get_db()
        users = db["users"]

        user = users.find_one({
            "reset_token_hash": token_hash,
            "reset_token_expires": {"$gt": now},
        })

        if not user:
            flash("Reset link is invalid or has expired.", "error")
            return redirect(url_for("auth.forgotpassword"))

        new_hash = generate_password_hash(new_password, method="scrypt", salt_length=16)

        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": new_hash}, "$unset": {"reset_token_hash": "", "reset_token_expires": ""}},
        )

        flash("Password updated. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("resetpassword.html")

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    profiles_collection = db["profiles"]

    if request.method == "POST":
        # Update profile data
        display_name = request.form.get("name")
        session_length_mins = int(request.form.get("studyPrefs.sessionLengthMins", 0))
        break_long_mins = int(request.form.get("studyPrefs.breakLongMins", 0))
        preferred_difficulty = request.form.get("studyPrefs.preferredDifficulty")
        updated_at = datetime.now(timezone.utc)

        profiles_collection.update_one(
            {"user_id": ObjectId(current_user.id)},
            {
                "$set": {
                    "displayName": display_name,
                    "studyPrefs": {
                        "sessionLengthMins": session_length_mins,
                        "breakLongMins": break_long_mins,
                        "preferredDifficulty": preferred_difficulty,
                    },
                    "updatedAt": updated_at,
                }
            },
        )
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    # Fetch the profile data for the logged-in user
    profile_data = profiles_collection.find_one({"user_id": ObjectId(current_user.id)})

    if not profile_data:
        # Create a new profile if it doesn't exist
        now = datetime.now(timezone.utc)
        profile_data = {
            "user_id": ObjectId(current_user.id),
            "displayName": current_user.name,
            "studyPrefs": {
                "sessionLengthMins": 25,
                "breakLongMins": 15,
                "preferredDifficulty": "medium",
            },
            "createdAt": now,
            "updatedAt": now,
        }
        profiles_collection.insert_one(profile_data)

    return render_template("profile.html", profile=profile_data)
