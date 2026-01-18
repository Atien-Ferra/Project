"""
Password management routes - update, forgot, and reset password.
"""
import os
import secrets
import hashlib
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from db import get_db
from . import auth_bp


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

        db = get_db()
        users = db["users"]
        user = users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("auth.login"))

        pepper = os.getenv("PASSWORD_PEPPER")
        if not check_password_hash(user.get("password"), current_password + pepper):
            flash("Current password is incorrect.", "error")
            return render_template("updatepassword.html")

        pepper_new_password = new_password + pepper
        new_hash = generate_password_hash(pepper_new_password, method="scrypt", salt_length=16)
        users.update_one({"_id": user["_id"]}, {"$set": {"password": new_hash}})

        flash("Password updated successfully. Please log in again.", "success")
        logout_user()
        return redirect(url_for("auth.login"))

    return render_template("updatepassword.html")


@auth_bp.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    """Handle password reset request."""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()

        db = get_db()
        users = db["users"]
        user = users.find_one({"email": email})

        if user:
            reset_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
            reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)

            users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "reset_token_hash": token_hash,
                        "reset_token_expires": reset_expires,
                    }
                },
            )

            reset_link = url_for("auth.reset_password", token=reset_token, _external=True)

            mail_server = os.getenv("MAIL_SERVER")
            mail_sent = False
            if mail_server:
                mail_port = int(os.getenv("MAIL_PORT", "587"))
                mail_username = os.getenv("MAIL_USERNAME")
                mail_password = os.getenv("MAIL_PASSWORD")
                mail_from = os.getenv("MAIL_FROM", mail_username or f"noreply@{mail_server}")
                use_tls = os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")

                subject = "Focus Flow password reset"
                body = (
                    f"Hi {user.get('name', '')},\n\n"
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
                            server.ehlo()
                            if use_tls:
                                server.starttls(context=ssl.create_default_context())
                                server.ehlo()
                            if mail_username and mail_password:
                                server.login(mail_username, mail_password)
                            server.send_message(msg)
                    mail_sent = True
                except Exception:
                    current_app.logger.exception("Failed to send password reset email")

            # In debug mode, log the reset link for testing (don't auto-redirect)
            if current_app.debug or os.getenv("SHOW_RESET_LINK") == "1":
                current_app.logger.info(f"Password reset link (debug): {reset_link}")

            # Only auto-redirect if explicitly enabled for development testing
            if os.getenv("DEV_REDIRECT_RESET") == "1":
                return redirect(url_for("auth.reset_password", token=reset_token))

        flash("If the email exists, a reset link has been sent", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgotpassword.html")


@auth_bp.route("/updatepassword/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    """Password reset using a token from reset link."""
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
