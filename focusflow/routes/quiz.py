import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from db import get_db
from ..services.files import allowed_file, extract_text_from_file
from ..services.questions import generate_questions_from_text_lmstudio

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    db = get_db()
    users = db["users"]

    user_doc = users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if not file or file.filename == "":
            flash("No file selected", "error")
            return redirect(url_for("quiz.dashboard"))

        if not allowed_file(file.filename):
            flash("Invalid file type. Upload PDF, DOCX, TXT, or images.", "error")
            return redirect(url_for("quiz.dashboard"))

        filename = secure_filename(file.filename)
        file_type = filename.rsplit(".", 1)[1].lower()
        temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(temp_path)

        extracted = extract_text_from_file(temp_path, file_type)
        if not extracted or not extracted.strip():
            try: os.remove(temp_path)
            except: pass
            flash("Could not read the file (empty/unreadable).", "error")
            return redirect(url_for("quiz.dashboard"))

        questions = generate_questions_from_text_lmstudio(extracted, num_questions=5)
        if not questions:
            try: os.remove(temp_path)
            except: pass
            flash("Could not generate questions. Upload a document with more content.", "error")
            return redirect(url_for("quiz.dashboard"))

        users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "current_file": {
                    "filename": filename,
                    "file_path": temp_path,
                    "file_type": file_type,
                    "uploaded_at": datetime.now(),
                },
                "current_questions": questions
            }}
        )

        flash("File uploaded successfully! Quiz generated.", "success")
        return redirect(url_for("quiz.quiz"))

    return render_template(
        "dashboard.html",
        user_name=current_user.name,
        streak=user_doc.get("streak", 0),
        quizzes_taken=user_doc.get("quizzes_taken", 0),
        tasks_done=user_doc.get("tasks_done", 0),
    )

@quiz_bp.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = (request.form.get("task_title") or "").strip()
    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("quiz.dashboard"))

    db = get_db()
    db["tasks"].insert_one({
        "user_id": ObjectId(current_user.id),
        "title": title,
        "done": False,
        "created_at": datetime.now(),
    })

    flash("Task added.", "success")
    return redirect(url_for("quiz.dashboard"))


@quiz_bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    db = get_db()
    users = db["users"]

    user_doc = users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    current_questions = user_doc.get("current_questions")
    if not current_questions:
        flash("No quiz generated yet. Upload a document first.", "error")
        return redirect(url_for("quiz.dashboard"))

    if request.method == "POST":
        score = 0
        for idx, q in enumerate(current_questions):
            user_answer = request.form.get(f"q{idx+1}")
            if user_answer == q.get("correct_answer"):
                score += 1

        total = len(current_questions)
        percentage = int((score / total) * 100) if total else 0
        passed = percentage >= 60

        # delete uploaded file
        try:
            cf = user_doc.get("current_file") or {}
            fp = cf.get("file_path")
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass

        update = {"$inc": {"quizzes_taken": 1}, "$unset": {"current_questions": "", "current_file": ""}}
        if passed:
            update["$inc"]["streak"] = 1
            update["$inc"]["tasks_done"] = 1

        users.update_one({"_id": ObjectId(current_user.id)}, update)

        return jsonify({"score": score, "total": total, "percentage": percentage, "passed": passed})

    return render_template("quiz.html", questions=current_questions)

@quiz_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    users = db["users"]

    user_doc = users.find_one({"_id": ObjectId(current_user.id)})
    if not user_doc:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()

        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("quiz.profile"))

        # prevent changing email to one that already exists
        exists = users.find_one({"email": email, "_id": {"$ne": ObjectId(current_user.id)}})
        if exists:
            flash("That email is already in use.", "error")
            return redirect(url_for("quiz.profile"))

        users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"name": name, "email": email}},
        )

        # keep Flask-Login user object in sync for the current request/session
        current_user.name = name
        current_user.email = email

        flash("Profile updated.", "success")
        return redirect(url_for("quiz.profile"))

    return render_template(
        "profile.html",
        user_name=user_doc.get("name", ""),
        user_email=user_doc.get("email", ""),
        streak=user_doc.get("streak", 0),
        quizzes_taken=user_doc.get("quizzes_taken", 0),
        tasks_done=user_doc.get("tasks_done", 0),
    )
