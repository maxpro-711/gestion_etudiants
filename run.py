"""Point d'entree local pour lancer Flask en mode dev."""
from app import create_app

# Application Flask creee via factory
app = create_app()

if __name__ == "__main__":
    # Lance le serveur de dev
    app.run(debug=True, host="0.0.0.0", port=5000)
