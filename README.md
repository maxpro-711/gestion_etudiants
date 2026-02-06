# Gestion des étudiants – PARTIE 1

## Description
Application Flask modulaire pour la gestion des étudiants, enseignants et notes.

## Lancer le projet
```bash
pip install -r requirements.txt
flask db upgrade
python run.py

## Admin par defaut
Par defaut :
- login : `admin`
- mot de passe : `admin123`

Tu peux changer ces valeurs via les variables d'environnement :
`ADMIN_LOGIN`, `ADMIN_PASSWORD`, `ADMIN_NOM`, `ADMIN_PRENOM`.
