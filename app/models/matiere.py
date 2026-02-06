from app.extensions import db


class Matiere(db.Model):
    """Matiere avec coefficient et credits."""

    __tablename__ = "matieres"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    coefficient = db.Column(db.Float, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
