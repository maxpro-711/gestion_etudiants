from datetime import datetime

from app.extensions import db


class Note(db.Model):
    """Note d'un etudiant, saisie par un enseignant."""

    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    valeur = db.Column(db.Float, nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    # Presence/absence et appreciation
    absence = db.Column(db.Boolean, default=False)
    appreciation = db.Column(db.Text, nullable=True)

    etudiant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    matiere_id = db.Column(
        db.Integer,
        db.ForeignKey("matieres.id"),
        nullable=False
    )

    enseignant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # Relations
    etudiant = db.relationship(
        "User",
        back_populates="notes",
        foreign_keys=[etudiant_id]
    )
    matiere = db.relationship("Matiere", backref="notes")
    enseignant = db.relationship(
        "User",
        foreign_keys=[enseignant_id]
    )
