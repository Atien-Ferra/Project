"""
Main routes - index page and error handlers.
"""
from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home page / landing page."""
    return render_template("index.html")


@main_bp.app_errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template("404.html"), 404


@main_bp.app_errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return render_template("500.html"), 500
