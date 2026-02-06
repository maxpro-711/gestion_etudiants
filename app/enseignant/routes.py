"""Routes enseignant: dashboard, notes par etudiant, CRUD notes."""
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.matiere import Matiere
from app.models.note import Note
from app.models.user import User
from . import enseignant_bp


def _require_enseignant():
    """Bloque l'acces si l'utilisateur courant n'est pas enseignant."""
    if current_user.role != "ENSEIGNANT":
        abort(403)


def _get_etudiant(etudiant_id: int) -> User:
    """Recupere un etudiant par id ou renvoie 404."""
    return User.query.filter_by(id=etudiant_id, role="ETUDIANT").first_or_404()


@enseignant_bp.route("/dashboard")
@login_required
def dashboard():
    _require_enseignant()

    # Stats filtrees par enseignant
    total_notes = Note.query.filter_by(enseignant_id=current_user.id).count()
    total_absences = Note.query.filter_by(
        enseignant_id=current_user.id,
        absence=True
    ).count()
    total_appreciations = Note.query.filter(
        Note.enseignant_id == current_user.id,
        Note.appreciation.isnot(None)
    ).count()

    etudiants_count = (
        db.session.query(Note.etudiant_id)
        .filter(Note.enseignant_id == current_user.id)
        .distinct()
        .count()
    )

    # Donnees pour cartes du dashboard
    stats = {
        "etudiants": etudiants_count,
        "matieres": len(current_user.matieres),
        "notes": total_notes,
        "absences": total_absences,
        "appreciations": total_appreciations
    }

    # Liste des etudiants pour selection
    etudiants = User.query.filter_by(role="ETUDIANT").all()

    return render_template(
        "enseignant/dashboard.html",
        stats=stats,
        etudiants=etudiants
    )


@enseignant_bp.route("/etudiants/<int:etudiant_id>/notes")
@login_required
def notes_etudiant(etudiant_id):
    _require_enseignant()

    etudiant = _get_etudiant(etudiant_id)
    # Notes saisies par l'enseignant courant uniquement
    notes = Note.query.filter_by(
        etudiant_id=etudiant.id,
        enseignant_id=current_user.id
    ).order_by(Note.date_ajout.desc()).all()

    return render_template(
        "enseignant/notes.html",
        etudiant=etudiant,
        notes=notes
    )


@enseignant_bp.route("/etudiants/<int:etudiant_id>/notes/add", methods=["GET", "POST"])
@login_required
def add_note_etudiant(etudiant_id):
    _require_enseignant()

    etudiant = _get_etudiant(etudiant_id)
    # Matieres deja notees par cet enseignant pour cet etudiant
    notes_etudiant = Note.query.filter_by(
        etudiant_id=etudiant.id,
        enseignant_id=current_user.id
    ).all()
    matieres_deja_notees = {n.matiere_id for n in notes_etudiant}
    # Matieres attribuees a l'enseignant
    matieres_assignees = list(current_user.matieres)
    matieres_disponibles = [
        m for m in matieres_assignees if m.id not in matieres_deja_notees
    ]

    if request.method == "POST":
        # Champs du formulaire
        matiere_id = request.form.get("matiere_id")
        valeur = request.form.get("valeur")
        absence = request.form.get("absence") == "on"
        appreciation = request.form.get("appreciation")

        # Bloquer double note pour la meme matiere
        try:
            matiere_id_int = int(matiere_id)
        except (TypeError, ValueError):
            flash("Matiere invalide")
            return redirect(url_for("enseignant.add_note_etudiant", etudiant_id=etudiant.id))

        if matiere_id_int not in {m.id for m in matieres_assignees}:
            flash("Matiere non attribuee a cet enseignant")
            return redirect(url_for("enseignant.add_note_etudiant", etudiant_id=etudiant.id))

        # Interdire une deuxieme note pour la meme matiere
        existing = Note.query.filter_by(
            etudiant_id=etudiant.id,
            matiere_id=matiere_id_int
        ).first()
        if existing:
            flash("Une note existe deja pour cette matiere")
            return redirect(url_for("enseignant.notes_etudiant", etudiant_id=etudiant.id))

        if (valeur is None or valeur == "") and not absence:
            flash("La note est obligatoire si l'etudiant est present")
            return redirect(url_for("enseignant.add_note_etudiant", etudiant_id=etudiant.id))

        # Validation note (0-20). Si absence cochee et valeur vide -> 0.
        if (valeur is None or valeur == "") and absence:
            valeur = 0

        try:
            valeur = float(valeur)
            if valeur < 0 or valeur > 20:
                raise ValueError
        except ValueError:
            flash("La note doit etre comprise entre 0 et 20")
            return redirect(url_for("enseignant.add_note_etudiant", etudiant_id=etudiant.id))

        note = Note(
            valeur=valeur,
            absence=absence,
            appreciation=appreciation,
            etudiant_id=etudiant.id,
            matiere_id=matiere_id_int,
            enseignant_id=current_user.id
        )

        db.session.add(note)
        db.session.commit()

        flash("Note enregistree")
        return redirect(url_for("enseignant.notes_etudiant", etudiant_id=etudiant.id))

    return render_template(
        "enseignant/add_note.html",
        etudiant=etudiant,
        matieres=matieres_disponibles
    )


@enseignant_bp.route("/notes")
@login_required
def notes_redirect():
    _require_enseignant()
    # Evite acces direct sans selection d'etudiant
    flash("Veuillez choisir un etudiant depuis le dashboard")
    return redirect(url_for("enseignant.dashboard"))


@enseignant_bp.route("/notes/add")
@login_required
def add_note_redirect():
    _require_enseignant()
    # Evite acces direct sans selection d'etudiant
    flash("Veuillez choisir un etudiant depuis le dashboard")
    return redirect(url_for("enseignant.dashboard"))


@enseignant_bp.route("/etudiants/<int:etudiant_id>/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note_etudiant(etudiant_id, note_id):
    _require_enseignant()

    etudiant = _get_etudiant(etudiant_id)
    # Note appartenant a cet enseignant uniquement
    note = Note.query.filter_by(
        id=note_id,
        etudiant_id=etudiant.id,
        enseignant_id=current_user.id
    ).first_or_404()
    # Matieres attribuees a l'enseignant (select)
    matieres = list(current_user.matieres)

    if request.method == "POST":
        # Champs du formulaire
        matiere_id = request.form.get("matiere_id")
        valeur = request.form.get("valeur")
        absence = request.form.get("absence") == "on"
        appreciation = request.form.get("appreciation")

        if (valeur is None or valeur == "") and not absence:
            flash("La note est obligatoire si l'etudiant est present")
            return redirect(url_for("enseignant.edit_note_etudiant", etudiant_id=etudiant.id, note_id=note.id))

        # Bloquer double note pour la meme matiere
        try:
            matiere_id_int = int(matiere_id)
        except (TypeError, ValueError):
            flash("Matiere invalide")
            return redirect(url_for("enseignant.edit_note_etudiant", etudiant_id=etudiant.id, note_id=note.id))

        if matiere_id_int not in {m.id for m in matieres}:
            flash("Matiere non attribuee a cet enseignant")
            return redirect(url_for("enseignant.edit_note_etudiant", etudiant_id=etudiant.id, note_id=note.id))

        # Interdire une autre note pour la meme matiere
        existing = Note.query.filter_by(
            etudiant_id=etudiant.id,
            matiere_id=matiere_id_int
        ).first()
        if existing and existing.id != note.id:
            flash("Une note existe deja pour cette matiere")
            return redirect(url_for("enseignant.edit_note_etudiant", etudiant_id=etudiant.id, note_id=note.id))

        if (valeur is None or valeur == "") and absence:
            valeur = 0

        try:
            valeur = float(valeur)
            if valeur < 0 or valeur > 20:
                raise ValueError
        except ValueError:
            flash("La note doit etre comprise entre 0 et 20")
            return redirect(url_for("enseignant.edit_note_etudiant", etudiant_id=etudiant.id, note_id=note.id))

        note.matiere_id = matiere_id_int
        note.valeur = valeur
        note.absence = absence
        note.appreciation = appreciation

        db.session.commit()
        flash("Note modifiee")
        return redirect(url_for("enseignant.notes_etudiant", etudiant_id=etudiant.id))

    return render_template(
        "enseignant/edit_note.html",
        etudiant=etudiant,
        note=note,
        matieres=matieres
    )


@enseignant_bp.route("/etudiants/<int:etudiant_id>/notes/<int:note_id>/delete")
@login_required
def delete_note_etudiant(etudiant_id, note_id):
    _require_enseignant()

    etudiant = _get_etudiant(etudiant_id)
    # Supprimer uniquement ses propres notes
    note = Note.query.filter_by(
        id=note_id,
        etudiant_id=etudiant.id,
        enseignant_id=current_user.id
    ).first_or_404()

    db.session.delete(note)
    db.session.commit()
    flash("Note supprimee")
    return redirect(url_for("enseignant.notes_etudiant", etudiant_id=etudiant.id))
