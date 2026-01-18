"""
Authentication routes module.
Handles login, signup, logout, and password management.
"""
import os
from flask import Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth_bp = Blueprint("auth", __name__)
limiter = Limiter(get_remote_address)

PEPPER = os.getenv("PASSWORD_PEPPER")
if not PEPPER:
    raise RuntimeError("PASSWORD_PEPPER not set")

# Import routes after blueprint is created to avoid circular imports
from .user import load_user
from .login import *
from .signup import *
from .password import *
from .profile import *
