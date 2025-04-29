import os
from flask import Flask, render_template, jsonify
import json

# Chargement des variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Initialisation de l'app Flask
app = Flask(__name__)

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUSPECTS_FILE = os.path.join(BASE_DIR, "suspects", "suspects.json")

# Chargement des identifiants Twitch
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/accounts")
def api_accounts():
    """Renvoie les comptes suspects au format JSON."""
    if os.path.exists(SUSPECTS_FILE):
        with open(SUSPECTS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    return jsonify(data)

# Main

if __name__ == "__main__":
    # Pour Fly.io ➔ utiliser le port donné par la variable d'environnement PORT
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
