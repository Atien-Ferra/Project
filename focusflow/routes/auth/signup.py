"""
User registration route.
"""
from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from werkzeug.security import generate_password_hash
from db import get_db
from . import auth_bp, get_pepper
from .user import User


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration."""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_with_pepper = password + get_pepper()
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
            "files": [],
            "created_at": datetime.now(timezone.utc)
        })
        user = User(str(result.inserted_id), name, email)
        login_user(user)
        flash("Account created successfully!", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("signup.html")
