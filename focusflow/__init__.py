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
    """
    Application Factory - creates and configures the Flask instance.
    """
    # Define paths for templates and static files relative to project root
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(basedir, ".."))

    # Load environment variables from .env file
    load_dotenv(os.path.join(project_root, ".env"))

    # Initialize Flask app with template and static paths
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "Templates", "HTML"),
        static_folder=os.path.join(project_root, "Static"),
    )
    
    # Core app configuration for session security and CSRF
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SESSION_COOKIE_HTTPONLY=True,       # Prevent JS access to session cookie
        SESSION_COOKIE_SAMESITE="Lax",      # CSRF protection: Lax is standard
        SESSION_COOKIE_SECURE=not app.debug,# Only send cookies over HTTPS in prod
        PERMANENT_SESSION_LIFETIME=timedelta(days=7), # Keep sessions for a week
        WTF_CSRF_CHECK_DEFAULT=False,       # We'll use manual CSRF check (see below)
    )

    # Initialize CSRF protection
    csrf.init_app(app)

    # Apply rate limiting globally to prevent brute force/abuse
    Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
    
    # Add security headers via Talisman
    Talisman(app, content_security_policy=None)

    # Set up upload folder configuration
    app.secret_key = os.getenv("SECRET_KEY")
    app.config["UPLOAD_FOLDER"] = os.path.join(project_root, "Static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16MB file limit

    # Create upload directory if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Configure Flask-Login for authentication
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" # Redirect here if @login_required fails

    # Register blueprints (modular route modules)
    app.register_blueprint(main_bp)      # Landing page
    app.register_blueprint(auth_bp)      # Auth system
    app.register_blueprint(quiz_bp)      # Quiz system
    app.register_blueprint(dashboard_bp) # Dashboard & internal API
    
    # Custom Request Hook for selective CSRF protection
    @app.before_request
    def csrf_protect():
        """
        Manually trigger CSRF protection for all mutating methods, 
        but exempt API routes which handle their own token check via custom headers if needed.
        """
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Skip CSRF for API routes (often used by mobile or external scripts)
            if request.path.startswith('/api/'):
                return
            # Check CSRF for standard form-based routes
            csrf.protect()
    
    # Standardised Error Handling for CSRF
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """
        Return JSON error for API calls, otherwise return 400 error page.
        """
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": "CSRF token missing or invalid"}), 400
        return render_template('500.html'), 400

    return app
