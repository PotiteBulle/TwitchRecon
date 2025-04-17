# TwitchRecon
Système de sentinelle Twitch pour repérer les comptes actifs liés à des attaques. Il interroge automatiquement l’API Twitch afin de détecter les pseudos créés en masse ou utilisés dans des contextes malveillants (spam, raids coordonnés, harcèlement). Les comptes identifiés sont consigné·es dans un fichier de veille structurés au format JSON (**suspects.json**)

## Fonctionnalités du System Twitch Recon

- Scan en continu de pseudos Twitch construits dynamiquement (patterns)
- Utilisation directe de l’API Twitch (OAuth2)
- Sauvegarde automatique des comptes trouvés dans `suspects/suspects.json`
- Journalisation détaillée dans `twitchrecon.log`
- Redémarrage automatique toutes les 5 minutes pour un nouveau cycle de recherche

---

## Arborescence du System Twitch Recon

```
TwitchRecon/
├── twitchrecon.py             # Script principal d’analyse en continu
├── patterns.json              # Liste des motifs de pseudos à surveiller
├── requirements.txt           # Dépendances Python
├── .env                       # Variables API Twitch (non versionné)
├── .gitignore                 # Ignore fichiers sensibles
├── twitchrecon.log            # Log de l’activité
└── suspects/
    └── suspects.json          # Résultats du scan
```

---

## Installation du System Twitch Recon

```bash
git clone https://github.com/PotiteBulle/TwitchRecon.git
cd TwitchRecon
pip install --break-system-packages -r requirements.txt # Passer par un system d'environnement, c'est plus sur (VENV)
```

---

## Configuration du System Twitch Recon

1. Crée un fichier `.env` à la racine avec :

```
CLIENT_ID=ton_client_id
CLIENT_SECRET=ton_client_secret
```

2. Ajoute un fichier `patterns.json` contenant : les prefixes & les sensitive_suffixes comme dans **Exemple de patterns là**

```json
{
  "prefixes": ["tuheur2", "exterminateur2", "chasseur2", "pourfendeur2"],
  "sensitive_suffixes": ["palestinian", "gazaoui", "hamasfree", "intifada"]
}
```

---

## Lancement du système Twitch Recon 

```bash
python3 twitchrecon.py
```

Le bot tournera en continu tant que tu ne l’arrêtes pas (`CTRL+C`).

---

## Licence

Ce projet est sous licence **[MIT](https://github.com/PotiteBulle/TwitchRecon/blob/main/LICENSE)**.  
Tu es libre de le modifier, distribuer, et l’utiliser dans tes projets.

---

## Crédit

Développé avec 💖 par [potate](https://github.com/PotiteBulle)