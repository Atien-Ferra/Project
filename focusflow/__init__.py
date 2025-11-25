import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import login_manager
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.quiz import quiz_bp

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(basedir, ".."))

    load_dotenv(os.path.join(project_root, ".env"))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "Templates", "HTML"),
        static_folder=os.path.join(project_root, "Static"),
    )

    app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    app.config["UPLOAD_FOLDER"] = os.path.join(project_root, "Static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)

    return app
