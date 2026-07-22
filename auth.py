"""
auth.py
--------------------
Authentication Blueprint
Handles:
- Register
- Login
- Logout
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db
from models import User

# Create Blueprint
auth_bp = Blueprint("auth", __name__)


# ==========================
# Home
# ==========================
@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    return render_template("index.html")


# ==========================
# Register
# ==========================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not all([name, email, password, confirm]):
            flash("Please fill all fields.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already registered.", "warning")
            return render_template("register.html")

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="Annotator"
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ==========================
# Login
# ==========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash("Welcome back!", "success")

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid Email or Password.", "danger")

    return render_template("login.html")




# ==========================
# Profile
# ==========================
@auth_bp.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html",
        user=current_user
    )
    # -------------------------------------------------
# Logout
# -------------------------------------------------

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))