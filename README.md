# Gestion des étudiants – PARTIE 1

## Description
Application Flask modulaire pour la gestion des étudiants, enseignants et notes.

## Lancer le projet
```bash
pip install -r requirements.txt
flask db upgrade
python run.py

L’application est accessible à l’adresse :
http://127.0.0.1:5000

Les matières par défaut sont créées automatiquement au premier lancement de l’application.

## Admin par defaut
Par defaut :
- login : `admin`
- mot de passe : `admin123`

Tu peux changer ces valeurs via les variables d'environnement :
`ADMIN_LOGIN`, `ADMIN_PASSWORD`, `ADMIN_NOM`, `ADMIN_PRENOM`.

## Dépannage rapide

- Si la commande `flask db upgrade` échoue, vérifiez que les dépendances sont bien installées et que l’environnement Flask est correctement configuré.

