# TwitchRecon System Dépendances
import os
import json
import time
import requests
import re
from dotenv import load_dotenv
from datetime import datetime

# Chargement de la configuration depuis le fichier .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Définition des chemins des dossiers et fichiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUSPECTS_DIR = os.path.join(BASE_DIR, "suspects")
LOG_FILE = os.path.join(BASE_DIR, "twitchrecon.log")
PATTERN_FILE = os.path.join(BASE_DIR, "patterns.json")
OUTPUT_FILE = os.path.join(SUSPECTS_DIR, "suspects.json")

# Création du dossier suspects s'il n'existe pas déjà
os.makedirs(SUSPECTS_DIR, exist_ok=True)

# URLs de l'API Twitch
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
USERS_URL = "https://api.twitch.tv/helix/users"

# Logger
def log(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except IOError as e:
        print(f"[LOG ERROR] Impossible d'écrire dans le fichier : {e}")

# Chargement de JSON
def load_json_file(filepath, default=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"[ERREUR] Chargement du fichier {filepath} : {e}")
    return default

# Vérification du format username
def is_valid_username(username):
    if len(username) > 25:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

# Récupération du token OAuth Twitch
def get_access_token():
    try:
        response = requests.post(TOKEN_URL, params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        })
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.RequestException as e:
        log(f"[ERREUR TOKEN] {e}")
        return None

# Génération des pseudos selon les patterns
def generate_usernames(prefixes, suffixes, separators, max_variants=50):
    usernames = set()
    for prefix in prefixes:
        usernames.add(prefix)
        for i in range(max_variants):
            usernames.add(f"{prefix}{i}")
        for suffix in suffixes:
            for sep in separators:
                usernames.add(f"{prefix}{sep}{suffix}")
                for i in range(max_variants):
                    usernames.add(f"{prefix}{sep}{suffix}{i}")
    return sorted(usernames)

# Vérifie si un compte existe sur Twitch
def check_username_exists(username, token):
    try:
        response = requests.get(USERS_URL, headers={
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }, params={"login": username})

        if response.status_code == 429:
            log("[RATE LIMIT] Trop de requêtes, pause de 1 minute...")
            time.sleep(60)
            return None

        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            user = data["data"][0]
            return {
                "username": user["login"],
                "id": user["id"],
                "display_name": user["display_name"],
                "checked_at": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
            }
    except requests.RequestException as e:
        log(f"[HTTP ERROR] {e}")
    return None

# Vérifie si le username correspond à prefix + sensitive suffix
def is_suspect(username, prefixes, suffixes):
    username = username.lower()
    for prefix in prefixes:
        for suffix in suffixes:
            if prefix + suffix in username:
                return True
    return False

# Main
if __name__ == "__main__":
    log("--- Lancement de TwitchRecon (mode filtré) ---")

    while True:
        try:
            token = get_access_token()
            if not token:
                log("[ERREUR] Impossible d'obtenir le token, nouvel essai dans 2 minutes.")
                time.sleep(120)
                continue

            patterns = load_json_file(PATTERN_FILE, default={})
            prefixes = patterns.get("prefixes", [])
            suffixes = patterns.get("sensitive_suffixes", [])
            keywords = patterns.get("contains_keywords", [])
            separators = patterns.get("separators", [""])

            usernames = generate_usernames(prefixes, suffixes, separators)
            known_users = load_json_file(OUTPUT_FILE, default=[])
            known_usernames = {user["username"] for user in known_users}

            for username in usernames:
                if username in known_usernames:
                    continue

                if not is_valid_username(username):
                    log(f"[INVALID] {username} non conforme, ignoré")
                    continue

                user_data = check_username_exists(username, token)
                if user_data:
                    # Seuls les comptes suspects (prefix+suffix) seront enregistrés
                    if is_suspect(user_data["username"], prefixes, suffixes):
                        log(f"[SUSPECT FLAGGED] {user_data['username']} enregistré")
                        known_users.append(user_data)
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(known_users, f, indent=2)
                    else:
                        log(f"[IGNORED] {user_data['username']} est valide mais non suspect")

                time.sleep(1)

            log("Nouveau cycle terminé. Pause avant relance...")
            time.sleep(300)

        except Exception as e:
            log(f"[ERREUR GENERALE] {e}")
            time.sleep(60)