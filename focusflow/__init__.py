"""
Focus Flow Application Factory
"""
import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask import render_template
from .extensions import login_manager
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.quiz import quiz_bp
from .routes.dashboard import dashboard_bp

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
        SESSION_COOKIE_SECURE=not app.debug,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        WTF_CSRF_CHECK_DEFAULT=False,  # We'll check manually where needed
    )

    csrf.init_app(app)

    Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
    Talisman(app, content_security_policy=None)

    app.secret_key = os.getenv("SECRET_KEY")
    app.config["UPLOAD_FOLDER"] = os.path.join(project_root, "Static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(dashboard_bp)
    
    # Exempt API routes from CSRF (they use token auth via session)
    @app.before_request
    def csrf_protect():
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Skip CSRF for API routes
            if request.path.startswith('/api/'):
                return
            # Check CSRF for non-API routes
            csrf.protect()
    
    # Handle CSRF errors gracefully for API
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": "CSRF token missing or invalid"}), 400
        return render_template('500.html'), 400

    return app
