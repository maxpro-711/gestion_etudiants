from app.extensions import db


class Classe(db.Model):
    """Classe academique (rattachee a une filiere)."""

    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    # Cle etrangere obligatoire vers la filiere
    filiere_id = db.Column(
        db.Integer,
        db.ForeignKey("filieres.id"),
        nullable=False
    )

    filiere = db.relationship(
        "Filiere",
        back_populates="classes"
    )

    etudiants = db.relationship(
        "User",
        back_populates="classe",
        cascade="all, delete"
    )
