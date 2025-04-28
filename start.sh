#!/bin/bash

# Activer l'environnement virtuel si besoin
# source venv/bin/activate

# Lancer TwitchRecon en arrière-plan
python3 twitchrecon.py &

# Lancer le Dashboard Flask
cd dashboard
python3 app.py