# app/utils/calculs.py

from collections import defaultdict


# ----------------------------
# A1.1 Moyenne d'une matiere
# ----------------------------
def moyenne_matiere(notes):
    """
    notes : liste de Note (meme matiere)
    Retourne la moyenne de la matiere (arrondie a 2 decimales)
    """
    if not notes:
        return 0.0

    total = sum(note.valeur for note in notes)
    moyenne = total / len(notes)

    return round(moyenne, 2)


# ----------------------------
# A1.2 Validation d'une matiere
# ----------------------------
def matiere_validee(moyenne):
    """
    Une matiere est validee si moyenne >= 10
    """
    return moyenne >= 10


# ----------------------------
# A1.3 Calcul des credits valides
# ----------------------------
def credits_matiere(moyenne, credits):
    """
    credits acquis uniquement si la matiere est validee
    """
    if moyenne >= 10:
        return credits
    return 0


# ----------------------------
# A1.4 Moyenne generale
# ----------------------------
def moyenne_generale(notes, use_coefficients=True):
    """
    notes : liste de Note (toutes matieres confondues)
    - Si use_coefficients = True : moyenne ponderee par coefficients
    - Sinon : moyenne simple des moyennes par matiere
    """

    if not notes:
        return 0.0

    notes_par_matiere = defaultdict(list)
    for note in notes:
        notes_par_matiere[note.matiere].append(note)

    if use_coefficients:
        total_points = 0.0
        total_coeffs = 0.0

        for matiere, notes_matiere in notes_par_matiere.items():
            coef = matiere.coefficient
            if coef is None or coef <= 0:
                continue

            moy = moyenne_matiere(notes_matiere)
            total_points += moy * coef
            total_coeffs += coef

        if total_coeffs == 0:
            return 0.0

        moyenne = total_points / total_coeffs
        return round(moyenne, 2)

    # Sans coefficients : moyenne des moyennes par matiere
    total_moyennes = 0.0
    total_matieres = 0

    for notes_matiere in notes_par_matiere.values():
        total_moyennes += moyenne_matiere(notes_matiere)
        total_matieres += 1

    if total_matieres == 0:
        return 0.0

    return round(total_moyennes / total_matieres, 2)


# ----------------------------
# A1.5 Bilan academique par etudiant
# ----------------------------
def bilan_academique(notes, use_coefficients=True):
    """
    notes : liste de Note d'un etudiant

    Retourne :
    - moyennes par matiere
    - credits valides
    - moyenne generale
    """

    notes_par_matiere = defaultdict(list)

    # Regrouper les notes par matiere
    for note in notes:
        notes_par_matiere[note.matiere].append(note)

    resultats_matieres = []
    total_credits = 0

    for matiere, notes_matiere in notes_par_matiere.items():
        moy = moyenne_matiere(notes_matiere)
        valide = matiere_validee(moy)
        credits = credits_matiere(moy, matiere.credits)

        total_credits += credits

        resultats_matieres.append({
            "matiere": matiere.nom,
            "moyenne": moy,
            "validee": valide,
            "credits": credits
        })

    moyenne_gen = moyenne_generale(notes, use_coefficients=use_coefficients)

    return {
        "matieres": resultats_matieres,
        "moyenne_generale": moyenne_gen,
        "credits_valides": total_credits
    }


# ----------------------------
# A2.1 Mention academique
# ----------------------------
def mention(moyenne):
    if moyenne < 10:
        return None
    if moyenne < 12:
        return "Passable"
    if moyenne < 14:
        return "Assez Bien"
    if moyenne < 16:
        return "Bien"
    return "Tres Bien"


# ----------------------------
# A2.2 Decision academique finale
# ----------------------------
def decision_academique(credits_valides, moyenne_generale, total_credits=60):
    """
    Determine la decision finale de l'etudiant
    """

    if credits_valides >= total_credits and moyenne_generale >= 10:
        return "ADMIS"

    if moyenne_generale >= 8:
        return "AJOURNE"

    return "REDOUBLE"


# ----------------------------
# A2.3 Resultat academique complet
# ----------------------------
def resultat_final(notes, use_coefficients=True):
    """
    Fonction maitre (celle que les routes doivent appeler)

    Retourne :
    - details par matiere
    - moyenne generale
    - credits valides
    - decision finale
    - mention
    """

    bilan = bilan_academique(notes, use_coefficients=use_coefficients)

    moyenne_gen = bilan["moyenne_generale"]
    credits = bilan["credits_valides"]

    decision = decision_academique(credits, moyenne_gen)
    mention_finale = mention(moyenne_gen) if decision == "ADMIS" else None

    return {
        "matieres": bilan["matieres"],
        "moyenne_generale": moyenne_gen,
        "credits_valides": credits,
        "decision": decision,
        "mention": mention_finale
    }
