"""Routes etudiant: dashboard, resultats, bulletin, demandes."""
from datetime import datetime
from io import BytesIO

from flask import render_template, abort, current_app, send_file, request, redirect, url_for, flash
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.extensions import db
from app.models.demande import Demande
from app.models.note import Note
from app.utils.calculs import resultat_final
from . import etudiant_bp


def _use_coefficients() -> bool:
    """Active ou non les coefficients dans les calculs."""
    return current_app.config.get("USE_COEFFICIENTS", True)


@etudiant_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "ETUDIANT":
        abort(403)

    # Toutes les notes de l'etudiant courant
    notes = Note.query.filter_by(etudiant_id=current_user.id).all()
    resultat = resultat_final(notes, use_coefficients=_use_coefficients())

    # Compte des absences
    total_absences = Note.query.filter_by(
        etudiant_id=current_user.id,
        absence=True
    ).count()

    # Cartes de stats
    stats = {
        "matieres": len(resultat["matieres"]),
        "notes": len(notes),
        "absences": total_absences,
        "moyenne": resultat["moyenne_generale"],
        "credits": resultat["credits_valides"],
        "decision": resultat["decision"]
    }

    return render_template(
        "etudiant/dashboard.html",
        stats=stats
    )


@etudiant_bp.route("/resultats")
@login_required
def resultats():
    if current_user.role != "ETUDIANT":
        abort(403)

    # Resultats detailles par matiere
    notes = Note.query.filter_by(etudiant_id=current_user.id).all()
    resultat = resultat_final(notes, use_coefficients=_use_coefficients())

    return render_template(
        "etudiant/resultats.html",
        resultat=resultat
    )


@etudiant_bp.route("/bulletin")
@login_required
def bulletin():
    if current_user.role != "ETUDIANT":
        abort(403)

    # Donnees a afficher dans le bulletin HTML
    notes = Note.query.filter_by(etudiant_id=current_user.id).all()
    resultat = resultat_final(notes, use_coefficients=_use_coefficients())

    return render_template(
        "etudiant/bulletin.html",
        resultat=resultat,
        now=datetime.now()
    )


@etudiant_bp.route("/bulletin/pdf")
@login_required
def bulletin_pdf():
    if current_user.role != "ETUDIANT":
        abort(403)

    # Donnees a injecter dans le PDF
    notes = Note.query.filter_by(etudiant_id=current_user.id).all()
    resultat = resultat_final(notes, use_coefficients=_use_coefficients())

    # Buffer en memoire pour generer le PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # En-tete du bulletin
    y = height - 50
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Bulletin de notes")
    y -= 20

    pdf.setFont("Helvetica", 10)
    identite = current_user.full_name or current_user.username
    pdf.drawString(40, y, f"Etudiant: {identite}")
    y -= 15
    pdf.drawString(40, y, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    y -= 25

    # Tableau des moyennes par matiere
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "Matiere")
    pdf.drawString(260, y, "Moyenne")
    pdf.drawString(340, y, "Credits")
    y -= 12
    pdf.setFont("Helvetica", 10)

    for item in resultat["matieres"]:
        # Saut de page si on arrive en bas
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(40, y, "Matiere")
            pdf.drawString(260, y, "Moyenne")
            pdf.drawString(340, y, "Credits")
            y -= 12
            pdf.setFont("Helvetica", 10)

        pdf.drawString(40, y, str(item["matiere"]))
        pdf.drawString(260, y, f'{item["moyenne"]:.2f}')
        pdf.drawString(340, y, str(item["credits"]))
        y -= 14

    # Resume global
    y -= 10
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, f'Moyenne generale: {resultat["moyenne_generale"]:.2f}')
    y -= 14
    pdf.drawString(40, y, f'Credits valides: {resultat["credits_valides"]}')
    y -= 14
    pdf.drawString(40, y, f'Decision: {resultat["decision"]}')
    y -= 14
    if resultat["mention"]:
        pdf.drawString(40, y, f'Mention: {resultat["mention"]}')

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="bulletin.pdf",
        mimetype="application/pdf"
    )


@etudiant_bp.route("/demandes", methods=["GET", "POST"])
@login_required
def demandes():
    if current_user.role != "ETUDIANT":
        abort(403)

    if request.method == "POST":
        # Demande saisie par l'etudiant
        objet = request.form.get("objet")
        message = request.form.get("message")

        if not objet or not message:
            flash("Objet et message sont obligatoires")
            return redirect(url_for("etudiant.demandes"))

        # Enregistrement de la demande
        demande = Demande(
            objet=objet,
            message=message,
            etudiant_id=current_user.id
        )
        db.session.add(demande)
        db.session.commit()
        flash("Demande envoyee")
        return redirect(url_for("etudiant.demandes"))

    # Liste des demandes existantes
    demandes = Demande.query.filter_by(etudiant_id=current_user.id).order_by(
        Demande.date_ajout.desc()
    ).all()

    return render_template("etudiant/demandes.html", demandes=demandes)
