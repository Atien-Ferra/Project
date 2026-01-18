"""
Login and logout routes.
"""
import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from db import get_db
from . import auth_bp
from .user import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
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
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid email or password", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("main.index"))
