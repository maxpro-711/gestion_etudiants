"""Routes admin: gestion filieres, classes, matieres, enseignants, etudiants."""
import os
import uuid
from flask import render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.classe import Classe
from app.models.filiere import Filiere
from app.models.matiere import Matiere
from app.models.user import User
from . import admin_bp

# Niveaux autorises pour les filieres
ALLOWED_NIVEAUX = {"L1", "L2", "L3"}
# Plafond global de credits (toutes matieres confondues)
MAX_TOTAL_CREDITS = 60
# Extensions d'images de profil autorisees
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def _normalize_niveau(value: str) -> str:
    """Nettoie et normalise le niveau (L1/L2/L3)."""
    if not value:
        return ""
    return value.strip().upper()


def _total_credits(exclude_id=None) -> int:
    """Somme des credits pour verifier la limite globale."""
    query = db.session.query(db.func.coalesce(db.func.sum(Matiere.credits), 0))
    if exclude_id is not None:
        query = query.filter(Matiere.id != exclude_id)
    return int(query.scalar() or 0)


def _allowed_image(filename: str) -> bool:
    """Valide les extensions d'images autorisees."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def _save_profile_image(file_storage):
    """Sauvegarde l'image de profil et retourne son nom unique."""
    if not file_storage or not file_storage.filename:
        return None
    if not _allowed_image(file_storage.filename):
        return None
    # Nom unique pour eviter collisions
    safe_name = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    file_storage.save(os.path.join(upload_dir, unique_name))
    return unique_name


def _require_admin():
    """Acces reserve a l'administrateur."""
    if current_user.role != "ADMIN":
        abort(403)


# -------------------------------
# DASHBOARD ADMIN
# -------------------------------
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    _require_admin()

    stats = {
        "filieres": Filiere.query.count(),
        "classes": Classe.query.count(),
        "matieres": Matiere.query.count(),
        "enseignants": User.query.filter_by(role="ENSEIGNANT").count(),
        "etudiants": User.query.filter_by(role="ETUDIANT").count(),
    }

    classes_list = Classe.query.all()
    matieres_list = Matiere.query.all()
    etudiants_list = User.query.filter_by(role="ETUDIANT").all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        classes=classes_list,
        matieres=matieres_list,
        etudiants=etudiants_list
    )


# -------------------------------
# LISTE DES FILIERES
# -------------------------------
@admin_bp.route("/filieres")
@login_required
def filieres():
    _require_admin()
    filieres = Filiere.query.all()
    return render_template("admin/filieres/index.html", filieres=filieres)


# -------------------------------
# AJOUT D'UNE FILIERE
# -------------------------------
@admin_bp.route("/filieres/add", methods=["GET", "POST"])
@login_required
def add_filiere():
    _require_admin()

    if request.method == "POST":
        nom = request.form.get("nom")
        niveau = _normalize_niveau(request.form.get("niveau"))
        annee = request.form.get("annee")

        if not nom or not niveau or not annee:
            flash("Tous les champs sont obligatoires")
            return redirect(url_for("admin.add_filiere"))
        if niveau not in ALLOWED_NIVEAUX:
            flash("Niveau invalide. Choisir L1, L2 ou L3.")
            return redirect(url_for("admin.add_filiere"))

        filiere = Filiere(nom=nom, niveau=niveau, annee=annee)
        db.session.add(filiere)
        db.session.commit()

        flash("Filiere ajoutee avec succes")
        return redirect(url_for("admin.filieres"))

    return render_template("admin/filieres/add.html")


# -------------------------------
# MODIFICATION D'UNE FILIERE
# -------------------------------
@admin_bp.route("/filieres/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_filiere(id):
    _require_admin()

    filiere = Filiere.query.get_or_404(id)

    if request.method == "POST":
        filiere.nom = request.form.get("nom")
        filiere.niveau = _normalize_niveau(request.form.get("niveau"))
        filiere.annee = request.form.get("annee")

        if not filiere.nom or not filiere.niveau or not filiere.annee:
            flash("Tous les champs sont obligatoires")
            return redirect(url_for("admin.edit_filiere", id=id))
        if filiere.niveau not in ALLOWED_NIVEAUX:
            flash("Niveau invalide. Choisir L1, L2 ou L3.")
            return redirect(url_for("admin.edit_filiere", id=id))

        db.session.commit()
        flash("Filiere modifiee avec succes")
        return redirect(url_for("admin.filieres"))

    return render_template("admin/filieres/edit.html", filiere=filiere)


# -------------------------------
# SUPPRESSION D'UNE FILIERE
# -------------------------------
@admin_bp.route("/filieres/delete/<int:id>")
@login_required
def delete_filiere(id):
    _require_admin()

    filiere = Filiere.query.get_or_404(id)
    db.session.delete(filiere)
    db.session.commit()

    flash("Filiere supprimee")
    return redirect(url_for("admin.filieres"))


# -------------------------------
# LISTE DES CLASSES
# -------------------------------
@admin_bp.route("/classes")
@login_required
def classes():
    _require_admin()

    classes = Classe.query.all()
    return render_template("admin/classes/index.html", classes=classes)


# -------------------------------
# AJOUT D'UNE CLASSE
# -------------------------------
@admin_bp.route("/classes/add", methods=["GET", "POST"])
@login_required
def add_classe():
    _require_admin()

    filieres = Filiere.query.all()

    if request.method == "POST":
        nom = request.form.get("nom")
        filiere_id = request.form.get("filiere_id")

        if not nom or not filiere_id:
            flash("Tous les champs sont obligatoires")
            return redirect(url_for("admin.add_classe"))

        classe = Classe(nom=nom, filiere_id=filiere_id)
        db.session.add(classe)
        db.session.commit()

        flash("Classe ajoutee avec succes")
        return redirect(url_for("admin.classes"))

    return render_template("admin/classes/add.html", filieres=filieres)


# -------------------------------
# MODIFICATION D'UNE CLASSE
# -------------------------------
@admin_bp.route("/classes/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_classe(id):
    _require_admin()

    classe = Classe.query.get_or_404(id)
    filieres = Filiere.query.all()

    if request.method == "POST":
        classe.nom = request.form.get("nom")
        classe.filiere_id = request.form.get("filiere_id")

        db.session.commit()
        flash("Classe modifiee avec succes")
        return redirect(url_for("admin.classes"))

    return render_template(
        "admin/classes/edit.html",
        classe=classe,
        filieres=filieres
    )


# -------------------------------
# SUPPRESSION D'UNE CLASSE
# -------------------------------
@admin_bp.route("/classes/delete/<int:id>")
@login_required
def delete_classe(id):
    _require_admin()

    classe = Classe.query.get_or_404(id)
    db.session.delete(classe)
    db.session.commit()

    flash("Classe supprimee")
    return redirect(url_for("admin.classes"))


# -------------------------------
# LISTE DES MATIERES
# -------------------------------
@admin_bp.route("/matieres")
@login_required
def matieres():
    _require_admin()

    matieres = Matiere.query.all()
    return render_template("admin/matieres/index.html", matieres=matieres)


# -------------------------------
# AJOUT D'UNE MATIERE
# -------------------------------
@admin_bp.route("/matieres/add", methods=["GET", "POST"])
@login_required
def add_matiere():
    _require_admin()

    if request.method == "POST":
        # Formulaire d'ajout de matiere
        nom = request.form.get("nom")
        coefficient_raw = request.form.get("coefficient")
        credits_raw = request.form.get("credits") or request.form.get("credit")

        if not nom:
            flash("Nom de la matiere obligatoire")
            return redirect(url_for("admin.add_matiere"))

        # Conversion types numeriques
        try:
            coefficient = float(coefficient_raw)
            credits = int(credits_raw)
        except (TypeError, ValueError):
            flash("Coefficient et credits doivent etre numeriques")
            return redirect(url_for("admin.add_matiere"))

        if credits <= 0:
            flash("Credits doit etre positif")
            return redirect(url_for("admin.add_matiere"))

        # Verifier plafond global (60 credits)
        total_credits = _total_credits()
        if total_credits + credits > MAX_TOTAL_CREDITS:
            flash(
                f"Total credits depasse {MAX_TOTAL_CREDITS} "
                f"(actuel: {total_credits})."
            )
            return redirect(url_for("admin.add_matiere"))

        matiere = Matiere(
            nom=nom,
            coefficient=coefficient,
            credits=credits
        )

        db.session.add(matiere)
        db.session.commit()

        flash("Matiere ajoutee avec succes")
        return redirect(url_for("admin.matieres"))

    return render_template("admin/matieres/add.html")


# -------------------------------
# MODIFICATION D'UNE MATIERE
# -------------------------------
@admin_bp.route("/matieres/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_matiere(id):
    _require_admin()

    matiere = Matiere.query.get_or_404(id)

    if request.method == "POST":
        # Edition d'une matiere existante
        matiere.nom = request.form.get("nom")

        coefficient_raw = request.form.get("coefficient")
        credits_raw = request.form.get("credits") or request.form.get("credit")

        if not matiere.nom:
            flash("Nom de la matiere obligatoire")
            return redirect(url_for("admin.edit_matiere", id=id))

        # Conversion types numeriques
        try:
            matiere.coefficient = float(coefficient_raw)
            matiere.credits = int(credits_raw)
        except (TypeError, ValueError):
            flash("Coefficient et credits doivent etre numeriques")
            return redirect(url_for("admin.edit_matiere", id=id))

        if matiere.credits <= 0:
            flash("Credits doit etre positif")
            return redirect(url_for("admin.edit_matiere", id=id))

        # Recalcul du total sans la matiere actuelle
        total_credits = _total_credits(exclude_id=id)
        if total_credits + matiere.credits > MAX_TOTAL_CREDITS:
            flash(
                f"Total credits depasse {MAX_TOTAL_CREDITS} "
                f"(actuel: {total_credits})."
            )
            return redirect(url_for("admin.edit_matiere", id=id))

        db.session.commit()
        flash("Matiere modifiee")
        return redirect(url_for("admin.matieres"))

    return render_template("admin/matieres/edit.html", matiere=matiere)


# -------------------------------
# SUPPRESSION D'UNE MATIERE
# -------------------------------
@admin_bp.route("/matieres/delete/<int:id>")
@login_required
def delete_matiere(id):
    _require_admin()

    matiere = Matiere.query.get_or_404(id)
    db.session.delete(matiere)
    db.session.commit()

    flash("Matiere supprimee")
    return redirect(url_for("admin.matieres"))


# -------------------------------
# LISTE DES ENSEIGNANTS
# -------------------------------
@admin_bp.route("/enseignants")
@login_required
def enseignants():
    _require_admin()

    enseignants = User.query.filter_by(role="ENSEIGNANT").all()
    return render_template(
        "admin/enseignants/index.html",
        enseignants=enseignants
    )


# -------------------------------
# AJOUT D'UN ENSEIGNANT
# -------------------------------
@admin_bp.route("/enseignants/add", methods=["GET", "POST"])
@login_required
def add_enseignant():
    _require_admin()

    matieres = Matiere.query.all()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        matiere_ids = request.form.getlist("matiere_ids")
        profile_image = _save_profile_image(request.files.get("profile_image"))

        if not username or not password:
            flash("Login et mot de passe sont obligatoires", "danger")
            return redirect(url_for("admin.add_enseignant"))

        if User.query.filter_by(username=username).first():
            flash("Ce nom d'utilisateur existe deja", "danger")
            return redirect(url_for("admin.add_enseignant"))

        enseignant = User(
            username=username,
            password_hash=generate_password_hash(password),
            role="ENSEIGNANT",
            nom=nom,
            prenom=prenom,
            profile_image=profile_image
        )

        if matiere_ids:
            enseignant.matieres = Matiere.query.filter(Matiere.id.in_(matiere_ids)).all()

        db.session.add(enseignant)
        db.session.commit()

        flash("Enseignant ajoute avec succes", "success")
        return redirect(url_for("admin.enseignants"))

    return render_template("admin/enseignants/add.html", matieres=matieres)


# -------------------------------
# MODIFICATION D'UN ENSEIGNANT
# -------------------------------
@admin_bp.route("/enseignants/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_enseignant(id):
    _require_admin()

    enseignant = User.query.filter_by(id=id, role="ENSEIGNANT").first_or_404()
    matieres = Matiere.query.all()
    matiere_ids_actuels = {m.id for m in enseignant.matieres}

    if request.method == "POST":
        new_username = request.form.get("username")
        if new_username and new_username != enseignant.username:
            if User.query.filter_by(username=new_username).first():
                flash("Nom d'utilisateur deja utilise")
                return redirect(url_for("admin.edit_enseignant", id=id))
            enseignant.username = new_username

        enseignant.nom = request.form.get("nom")
        enseignant.prenom = request.form.get("prenom")
        matiere_ids = request.form.getlist("matiere_ids")
        enseignant.matieres = Matiere.query.filter(Matiere.id.in_(matiere_ids)).all()
        profile_image = _save_profile_image(request.files.get("profile_image"))
        if profile_image:
            enseignant.profile_image = profile_image

        password = request.form.get("password")
        if password:
            enseignant.password_hash = generate_password_hash(password)

        db.session.commit()
        flash("Enseignant modifie")
        return redirect(url_for("admin.enseignants"))

    return render_template(
        "admin/enseignants/edit.html",
        enseignant=enseignant,
        matieres=matieres,
        matiere_ids_actuels=matiere_ids_actuels
    )


# -------------------------------
# SUPPRESSION D'UN ENSEIGNANT
# -------------------------------
@admin_bp.route("/enseignants/delete/<int:id>")
@login_required
def delete_enseignant(id):
    _require_admin()

    enseignant = User.query.filter_by(id=id, role="ENSEIGNANT").first_or_404()
    db.session.delete(enseignant)
    db.session.commit()

    flash("Enseignant supprime")
    return redirect(url_for("admin.enseignants"))


# -------------------------------
# LISTE DES ETUDIANTS
# -------------------------------
@admin_bp.route("/etudiants")
@login_required
def etudiants():
    _require_admin()

    etudiants = User.query.filter_by(role="ETUDIANT").all()
    return render_template(
        "admin/etudiants/index.html",
        etudiants=etudiants
    )


# -------------------------------
# AJOUT D'UN ETUDIANT
# -------------------------------
@admin_bp.route("/etudiants/add", methods=["GET", "POST"])
@login_required
def add_etudiant():
    _require_admin()

    classes = Classe.query.all()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        matricule = request.form.get("matricule")
        classe_id = request.form.get("classe_id")
        profile_image = _save_profile_image(request.files.get("profile_image"))

        if not username or not password or not nom or not prenom or not matricule or not classe_id:
            flash("Tous les champs sont obligatoires")
            return redirect(url_for("admin.add_etudiant"))

        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur deja utilise")
            return redirect(url_for("admin.add_etudiant"))

        if User.query.filter_by(matricule=matricule).first():
            flash("Matricule deja utilise")
            return redirect(url_for("admin.add_etudiant"))

        etudiant = User(
            username=username,
            password_hash=generate_password_hash(password),
            role="ETUDIANT",
            nom=nom,
            prenom=prenom,
            matricule=matricule,
            classe_id=classe_id,
            profile_image=profile_image
        )

        db.session.add(etudiant)
        db.session.commit()

        flash("Etudiant ajoute avec succes")
        return redirect(url_for("admin.etudiants"))

    return render_template(
        "admin/etudiants/add.html",
        classes=classes
    )


# -------------------------------
# MODIFICATION D'UN ETUDIANT
# -------------------------------
@admin_bp.route("/etudiants/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_etudiant(id):
    _require_admin()

    etudiant = User.query.filter_by(id=id, role="ETUDIANT").first_or_404()
    classes = Classe.query.all()

    if request.method == "POST":
        new_username = request.form.get("username")
        if new_username and new_username != etudiant.username:
            if User.query.filter_by(username=new_username).first():
                flash("Nom d'utilisateur deja utilise")
                return redirect(url_for("admin.edit_etudiant", id=id))
            etudiant.username = new_username

        etudiant.nom = request.form.get("nom")
        etudiant.prenom = request.form.get("prenom")
        new_matricule = request.form.get("matricule")
        if new_matricule and new_matricule != etudiant.matricule:
            if User.query.filter_by(matricule=new_matricule).first():
                flash("Matricule deja utilise")
                return redirect(url_for("admin.edit_etudiant", id=id))
            etudiant.matricule = new_matricule

        etudiant.classe_id = request.form.get("classe_id")
        profile_image = _save_profile_image(request.files.get("profile_image"))
        if profile_image:
            etudiant.profile_image = profile_image

        password = request.form.get("password")
        if password:
            etudiant.password_hash = generate_password_hash(password)

        db.session.commit()
        flash("Etudiant modifie")
        return redirect(url_for("admin.etudiants"))

    return render_template(
        "admin/etudiants/edit.html",
        etudiant=etudiant,
        classes=classes
    )


# -------------------------------
# SUPPRESSION D'UN ETUDIANT
# -------------------------------
@admin_bp.route("/etudiants/delete/<int:id>")
@login_required
def delete_etudiant(id):
    _require_admin()

    etudiant = User.query.filter_by(id=id, role="ETUDIANT").first_or_404()
    db.session.delete(etudiant)
    db.session.commit()

    flash("Etudiant supprime")
    return redirect(url_for("admin.etudiants"))
