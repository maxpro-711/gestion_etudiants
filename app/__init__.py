import os
from flask import Flask, render_template, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import OperationalError

from app.config import Config
from app.extensions import db, migrate, login_manager
from app.models.user import User
from app.seed import seed_defaults


def create_app():
    """Factory principale de l'application Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # -----------------------
    # Initialisation extensions (DB, migrations, login)
    # -----------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # -----------------------
    # Import des modeles (IMPORTANT pour SQLAlchemy)
    # -----------------------
    from app.models import user, filiere, classe, matiere, note, demande

    # -----------------------
    # Import & enregistrement des blueprints (routes)
    # -----------------------
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.enseignant.routes import enseignant_bp
    from app.etudiant.routes import etudiant_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(enseignant_bp, url_prefix="/enseignant")
    app.register_blueprint(etudiant_bp, url_prefix="/etudiant")

    # -----------------------
    # Route d'accueil (redirection selon role)
    # -----------------------
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            if current_user.role == "ADMIN":
                return redirect(url_for("admin.dashboard"))
            if current_user.role == "ENSEIGNANT":
                return redirect(url_for("enseignant.dashboard"))
            if current_user.role == "ETUDIANT":
                return redirect(url_for("etudiant.dashboard"))

        return render_template("home.html")

    # -----------------------
    # Seed admin + donnees de base (matieres, etc.)
    # -----------------------
    with app.app_context():
        create_admin_if_not_exists()
        seed_defaults()

    # Dossier pour stocker les photos de profil
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app


def create_admin_if_not_exists():
    """Cree un admin par defaut si aucun admin n'existe."""
    try:
        admin = User.query.filter_by(role="ADMIN").first()
        if not admin:
            login = current_app.config.get("DEFAULT_ADMIN_LOGIN", "admin")
            password = current_app.config.get("DEFAULT_ADMIN_PASSWORD", "admin123")
            nom = current_app.config.get("DEFAULT_ADMIN_NOM", "Admin")
            prenom = current_app.config.get("DEFAULT_ADMIN_PRENOM", "System")

            admin = User(
                username=login,
                password_hash=generate_password_hash(password),
                role="ADMIN",
                nom=nom,
                prenom=prenom
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin cree automatiquement :", login)
    except OperationalError:
        # Tables non encore creees (migration en cours)
        pass
