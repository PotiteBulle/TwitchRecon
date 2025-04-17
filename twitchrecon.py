# TwitchRecon System Dépendances
import os
import json
import time
import requests
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

# Logger : écrit les logs dans le terminal et dans un fichier
def log(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

# Chargement des patterns (préfixes, suffixes, mots-clés sensibles)
def load_patterns():
    with open(PATTERN_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Obtention d'un token d'accès OAuth depuis l'API Twitch
def get_access_token():
    response = requests.post(TOKEN_URL, params={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    })
    response.raise_for_status()
    return response.json()["access_token"]

# Génération des pseudos à tester selon les patterns
def generate_usernames(prefixes, suffixes, max_suffix_variants=50):
    usernames = set()
    for prefix in prefixes:
        usernames.add(prefix)
        for i in range(max_suffix_variants):
            usernames.add(f"{prefix}{i}")
        for suffix in suffixes:
            usernames.add(f"{prefix}{suffix}")
            for i in range(max_suffix_variants):
                usernames.add(f"{prefix}{suffix}{i}")
    return list(usernames)

# Vérifie si un pseudo Twitch existe via l'API
def check_username_exists(username, token):
    response = requests.get(USERS_URL, headers={
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }, params={"login": username})
    data = response.json()
    if "data" in data and data["data"]:
        return {
            "username": data["data"][0]["login"],
            "id": data["data"][0]["id"],
            "display_name": data["data"][0]["display_name"],
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    return None

# Chargement des utilisateurices déjà enregistrés dans suspects.json
def load_existing_users():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Sauvegarde des utilisateurices détectés
def save_users(users):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

# Vérifie si le pseudo contient un mot-clé sensible (peu importe sa position)
def contains_sensitive_keyword(username, keywords):
    lower_username = username.lower()
    return any(keyword.lower() in lower_username for keyword in keywords)

# Fonction principale de surveillance continue
if __name__ == "__main__":
    log("--- Lancement de TwitchRecon (mode continu) ---")

    while True:
        try:
            # Authentification
            token = get_access_token()
            # Chargement des règles de détection
            patterns = load_patterns()

            prefixes = patterns.get("prefixes", [])
            suffixes = patterns.get("sensitive_suffixes", [])
            keywords = patterns.get("contains_keywords", [])
            usernames = generate_usernames(prefixes, suffixes)

            # Chargement des utilisateurs déjà connus
            known_users = load_existing_users()
            known_usernames = {u["username"] for u in known_users}

            # Boucle sur tous les pseudos générés
            for username in usernames:
                if username in known_usernames:
                    log(f"[SKIP] {username} déjà connu")
                    continue

                user_data = check_username_exists(username, token)
                if user_data:
                    if contains_sensitive_keyword(username, keywords):
                        log(f"[FLAGGED] {username} contient un mot-clé sensible")
                    else:
                        log(f"[FOUND] {username} ajouté")

                    known_users.append(user_data)
                    save_users(known_users)
                else:
                    log(f"[NOT FOUND] {username}")

                time.sleep(1)

            log("Nouveau cycle de scan terminé. Attente avant relance...")
            time.sleep(300)  # Pause de 5 minutes entre chaque boucle

        except Exception as e:
            log(f"[ERREUR] {str(e)}")
            time.sleep(60)  # Pause d'1 min en cas d'erreur