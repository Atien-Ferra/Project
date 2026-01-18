"""
Focus session API endpoint.
"""
from flask import request, jsonify
from flask_login import login_required, current_user
from ...services.focus import record_focus_session
from . import dashboard_bp


@dashboard_bp.route("/api/focus/log", methods=["POST"])
@login_required
def log_focus_session():
    """Log a completed focus session."""
    data = request.get_json()
    mode = data.get("mode")
    duration = data.get("duration")
    
    if not mode or not duration:
        return jsonify({"success": False, "error": "Missing session data"}), 400
        
    session_id = record_focus_session(current_user.id, mode, duration)
    
    return jsonify({
        "success": True,
        "session_id": session_id
    }), 200
