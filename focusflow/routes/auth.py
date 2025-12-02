import os, secrets, hashlib
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..extensions import login_manager
from db import get_db

auth_bp = Blueprint("auth", __name__)

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
        email = request.form.get("email")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        db = get_db()
        user_doc = db["users"].find_one({"email": email})
        if user_doc and check_password_hash(user_doc["password"], password):
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
        email = (request.form.get("email") or "").strip().lower()

        # Always show success to avoid leaking whether an email exists
        msg = "If the email exists, a reset link has been sent."

        if not email:
            flash(msg, "success")
            return redirect(url_for("auth.login"))

        db = get_db()
        users = db["users"]
        user = users.find_one({"email": email})

        if user:
            # 1) create token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

            # 2) store hashed token + expiry
            users.update_one(
                {"_id": user["_id"]},
                {"$set": {"reset_token_hash": token_hash, "reset_token_expires": expires_at}},
            )

            # 3) build link
            reset_link = url_for("auth.reset_password", token=token, _external=True)

            # TODO: send email here with reset_link.
            # For development, log it:
            current_app.logger.warning("Password reset link for %s: %s", email, reset_link)

        flash(msg, "success")
        return redirect(url_for("auth.login"))

    return render_template("forgotpassword.html")



@auth_bp.route('/updatepassword', methods=['GET', 'POST'])
@login_required
def updatepassword():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user_email = current_user.id
        user_data = users.get(user_email)
        
        if user_data and user_data['password'] == current_password:
            if new_password == confirm_password:
                users[user_email]['password'] = new_password
                flash('Password updated successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('New passwords do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('updatepassword.html')
