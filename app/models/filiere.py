from app.extensions import db


class Filiere(db.Model):
    """Filiere academique (ex: Licence L1/L2/L3)."""

    __tablename__ = "filieres"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    niveau = db.Column(db.String(10), nullable=False)
    annee = db.Column(db.String(20), nullable=False)

    classes = db.relationship(
        "Classe",
        back_populates="filiere",
        cascade="all, delete"
    )
