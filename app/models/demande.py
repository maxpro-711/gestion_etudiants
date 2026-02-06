from datetime import datetime

from app.extensions import db


class Demande(db.Model):
    """Demande soumise par un etudiant."""
    __tablename__ = "demandes"

    id = db.Column(db.Integer, primary_key=True)
    objet = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    statut = db.Column(db.String(20), default="EN_ATTENTE", nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    etudiant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    etudiant = db.relationship("User", back_populates="demandes")
