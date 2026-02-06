"""Auth routes: login/logout and session loading."""
from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from app.extensions import login_manager
from app.models.user import User
from . import auth_bp


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to load a user from the session."""
    return User.query.get(int(user_id))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user and redirect to the correct dashboard."""
    if request.method == "POST":
        # Credentials from the login form
        username = request.form.get("username")
        password = request.form.get("password")

        # Fetch user by username
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Open session
            login_user(user)

            # Redirection selon le role
            if user.role == "ADMIN":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "ENSEIGNANT":
                return redirect(url_for("enseignant.dashboard"))
            elif user.role == "ETUDIANT":
                return redirect(url_for("etudiant.dashboard"))

        # Invalid credentials
        flash("Identifiants incorrects")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Clear session and go back to login."""
    logout_user()
    return redirect(url_for("auth.login"))
