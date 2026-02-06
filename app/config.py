import os
from datetime import date


def _default_academic_year() -> str:
    """
    Retourne une annee academique du type 2025-2026.
    Regle simple : si mois >= 9, annee = N-(N+1) sinon (N-1)-N.
    """
    today = date.today()
    start_year = today.year if today.month >= 9 else today.year - 1
    return f"{start_year}-{start_year + 1}"


class Config:
    """Configuration centrale de l'application."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Base de donnees par defaut dans instance/
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "gestion_etudiants.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Parametrage global (moyennes et annees)
    USE_COEFFICIENTS = os.environ.get("USE_COEFFICIENTS", "true").lower() == "true"
    DEFAULT_ANNEE = os.environ.get("DEFAULT_ANNEE", _default_academic_year())

    # Admin par defaut (peut etre surcharge en environnement)
    DEFAULT_ADMIN_LOGIN = os.environ.get("ADMIN_LOGIN", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
    DEFAULT_ADMIN_NOM = os.environ.get("ADMIN_NOM", "Admin")
    DEFAULT_ADMIN_PRENOM = os.environ.get("ADMIN_PRENOM", "System")

    # Uploads (photos de profil)
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "app", "static", "uploads")
    )
