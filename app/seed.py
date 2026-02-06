"""Seed des donnees par defaut (matieres)."""
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.models.matiere import Matiere


# Total credits = 60 (conforme au cahier des charges)
TOTAL_CREDITS = 60
DEFAULT_MATIERES = [
    {"nom": "Algorithme", "coefficient": 3, "credits": 8},
    {"nom": "Base de donnees", "coefficient": 3, "credits": 8},
    {"nom": "Framework web", "coefficient": 3, "credits": 8},
    {"nom": "Gestion de projets", "coefficient": 2, "credits": 6},
    {"nom": "Anglais", "coefficient": 2, "credits": 6},
    {"nom": "Technique de communication", "coefficient": 2, "credits": 6},
    {"nom": "Droit", "coefficient": 2, "credits": 6},
    {"nom": "Reseau Telecom", "coefficient": 2, "credits": 6},
    {"nom": "Electronique", "coefficient": 2, "credits": 6},
]


def seed_defaults():
    """Point d'entree du seed (ignore si les tables n'existent pas)."""
    try:
        _seed_matieres()
    except OperationalError:
        # Tables non encore creees (migration en cours)
        pass


def _seed_matieres():
    """Ajoute les matieres manquantes sans dupliquer."""
    existing = {m.nom for m in Matiere.query.all()}
    added = False
    _validate_total_credits()

    # Ajouter seulement les matieres absentes
    for matiere in DEFAULT_MATIERES:
        if matiere["nom"] in existing:
            continue
        db.session.add(
            Matiere(
                nom=matiere["nom"],
                coefficient=matiere["coefficient"],
                credits=matiere["credits"]
            )
        )
        added = True

    if added:
        db.session.commit()


def _validate_total_credits():
    """Verifie que le total des credits vaut 60."""
    total = sum(m["credits"] for m in DEFAULT_MATIERES)
    if total != TOTAL_CREDITS:
        raise ValueError(
            f"Total credits invalide: {total}. Attendu: {TOTAL_CREDITS}."
        )
