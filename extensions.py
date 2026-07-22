"""
extensions.py
----------------
Initialize Flask extensions.

This file creates extension objects that are shared
throughout the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Database
db = SQLAlchemy()

# Login Manager
login_manager = LoginManager()

# Redirect users to login page if authentication is required
login_manager.login_view = "auth.login"

# Flash message shown when login is required
login_manager.login_message = "Please login to continue."

# Bootstrap style (optional)
login_manager.login_message_category = "warning"