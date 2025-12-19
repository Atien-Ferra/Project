import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import login_manager
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.quiz import quiz_bp
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

csrf = CSRFProtect()

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(basedir, ".."))

    load_dotenv(os.path.join(project_root, ".env"))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "Templates", "HTML"),
        static_folder=os.path.join(project_root, "Static"),
    )
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not app.debug,      # True in production (HTTPS)
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    )

    csrf.init_app(app)

    Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
    Talisman(app, content_security_policy=None)  # start simple; add CSP later

    app.secret_key = os.getenv("SECRET_KEY")
    app.config["UPLOAD_FOLDER"] = os.path.join(project_root, "Static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)

    return app
