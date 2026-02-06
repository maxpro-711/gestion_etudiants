# Gestion des etudiants – PARTIE 1

## Description
Application Flask modulaire pour la gestion des etudiants, enseignants et notes.

## Lancer le projet
```bash
pip install -r requirements.txt
python run.py
```

## Migrations (schema)
Si tu modifies les modeles, pense a appliquer les migrations :
```bash
flask db upgrade
```

## Admin par defaut
Par defaut :
- login : `admin`
- mot de passe : `admin123`

Tu peux changer ces valeurs via les variables d'environnement :
`ADMIN_LOGIN`, `ADMIN_PASSWORD`, `ADMIN_NOM`, `ADMIN_PRENOM`.
