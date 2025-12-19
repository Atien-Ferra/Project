import os, secrets, hashlib, smtplib, ssl
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from email.message import EmailMessage
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


@auth_bp.route("/updatepassword", methods=["GET", "POST"])
@login_required
def updatepassword():
    """Logged-in user password update (requires current password)."""
    if request.method == "POST":
        current_password = request.form.get("current_password") or ""
        new_password = request.form.get("new_password") or ""
        confirm = request.form.get("confirm_password") or ""

        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("updatepassword.html")

        if new_password != confirm:
            flash("New passwords do not match.", "error")
            return render_template("updatepassword.html")

        # Verify current password
        db = get_db()
        users = db["users"]
        user = users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("auth.login"))

        pepper = os.getenv("PASSWORD_PEPPER")
        if not check_password_hash(user.get("password"), (current_password) + pepper):
            flash("Current password is incorrect.", "error")
            return render_template("updatepassword.html")

        pepper_new_password = new_password + pepper
        new_hash = generate_password_hash(pepper_new_password, method="scrypt", salt_length=16)
        users.update_one({"_id": user["_id"]}, {"$set": {"password": new_hash}})

        flash("Password updated successfully. Please log in again.", "success")
        # Log user out so they can re-login with new password
        logout_user()
        return redirect(url_for("auth.login"))

    return render_template("updatepassword.html")

@auth_bp.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()

        db = get_db()
        users = db["users"]
        user = users.find_one({"email": email})

        # Always show the same message for security (don't reveal if email exists)
        if user:
            # Generate a secure reset token
            reset_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
            reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)

            # Store token hash and expiration in database
            users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "reset_token_hash": token_hash,
                        "reset_token_expires": reset_expires,
                    }
                },
            )

            # Build the reset link (external URL)
            reset_link = url_for("auth.reset_password", token=reset_token, _external=True)

            # Try to send an email if SMTP settings are provided
            mail_server = os.getenv("MAIL_SERVER")
            mail_sent = False
            if mail_server:
                mail_port = int(os.getenv("MAIL_PORT", "587"))
                mail_username = os.getenv("MAIL_USERNAME")
                mail_password = os.getenv("MAIL_PASSWORD")
                mail_from = os.getenv("MAIL_FROM", mail_username or f"noreply@{mail_server}")
                use_tls = os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")

                current_app.logger.info(
                    "SMTP cfg server=%r port=%r tls=%r user=%r from=%r",
                    mail_server, mail_port, use_tls, mail_username, mail_from
                )

                subject = "Focus Flow password reset"
                body = (
                    f"Hi {user.get('name','')},\n\n"
                    "You requested a password reset. Use the link below to reset your password:\n\n"
                    f"{reset_link}\n\n"
                    "This link expires in 1 hour. If you did not request this, you can ignore this email.\n"
                )

                msg = EmailMessage()
                msg["Subject"] = subject
                msg["From"] = mail_from
                msg["To"] = user["email"]
                msg.set_content(body)

                try:
                    if mail_port == 465:
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(mail_server, mail_port, context=context) as server:
                            if mail_username and mail_password:
                                server.login(mail_username, mail_password)
                            server.send_message(msg)
                    else:
                        with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
                            server.set_debuglevel(1)
                            server.ehlo()
                            if use_tls:
                                server.starttls(context=ssl.create_default_context())
                                server.ehlo()
                            if mail_username and mail_password:
                                server.login(mail_username, mail_password)
                            server.send_message(msg)
                    mail_sent = True
                    current_app.logger.info("Password reset email sent to %s", user["email"])
                except Exception:
                    current_app.logger.exception("Failed to send password reset email")

            # Optionally log the reset link for debugging when SHOW_RESET_LINK=1
            if current_app.debug  or os.getenv("SHOW_RESET_LINK") == "1":
                return redirect(url_for("auth.reset_password", token=reset_token))

            if mail_server and not mail_sent:
                current_app.logger.warning(
                    "MAIL_SERVER is set but sending failed; check MAIL_* env vars and network connectivity"
                )

            # For development convenience, optionally redirect directly to the reset page
            # Only enable this when DEV_REDIRECT_RESET=1 to avoid accidental redirects in debug
            if os.getenv("DEV_REDIRECT_RESET") == "1":
                # Redirect to internal reset view with the token so you can complete the flow
                return redirect(url_for("auth.reset_password", token=reset_token))

        flash("If the email exists, a reset link has been sent", "success")
        return redirect(url_for("auth.login"))
    return render_template("forgotpassword.html")


@auth_bp.route("/updatepassword/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    """
    Password reset using a token included in the reset link.
    Renders the same `updatepassword.html` template but with a token variable so
    the form posts back to this tokenized URL.
    """
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("updatepassword.html", token=token)

        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("updatepassword.html", token=token)

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
        pepper = os.getenv("PASSWORD_PEPPER")
        new_hash = generate_password_hash(new_password + pepper, method="scrypt", salt_length=16)

        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": new_hash}, "$unset": {"reset_token_hash": "", "reset_token_expires": ""}},
        )

        flash("Password updated. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("updatepassword.html", token=token)
