from app.extensions import db
from flask_login import UserMixin

# Table d'association (many-to-many) entre enseignants et matieres
enseignant_matieres = db.Table(
    "enseignant_matieres",
    db.Column("enseignant_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("matiere_id", db.Integer, db.ForeignKey("matieres.id"), primary_key=True),
)


class User(db.Model, UserMixin):
    """Modele utilisateur pour admin/enseignant/etudiant."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Donnees utilisateur (conformes au cahier des charges)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=True)
    prenom = db.Column(db.String(100), nullable=True)
    matricule = db.Column(db.String(50), unique=True, nullable=True)  # uniquement ETUDIANT
    profile_image = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # uniquement pour ETUDIANT
    classe_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=True)
    classe = db.relationship(
        "Classe",
        back_populates="etudiants"
    )

    notes = db.relationship(
        "Note",
        back_populates="etudiant",
        cascade="all, delete-orphan",
        foreign_keys="Note.etudiant_id"
    )

    # Notes saisies par l'enseignant
    notes_saisies = db.relationship(
        "Note",
        foreign_keys="Note.enseignant_id"
    )

    demandes = db.relationship(
        "Demande",
        back_populates="etudiant",
        cascade="all, delete-orphan"
    )

    # Matieres attribuees a l'enseignant
    matieres = db.relationship(
        "Matiere",
        secondary=enseignant_matieres,
        backref=db.backref("enseignants", lazy="dynamic")
    )

    @property
    def login(self) -> str:
        """Alias conforme au cahier des charges (login = username)."""
        return self.username

    @login.setter
    def login(self, value: str) -> None:
        self.username = value

    @property
    def full_name(self) -> str:
        parts = [self.prenom or "", self.nom or ""]
        return " ".join(p for p in parts if p).strip()
