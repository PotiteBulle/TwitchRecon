@echo off

REM Activer l'environnement virtuel si besoin
REM call venv\Scripts\activate.bat

REM Lancer TwitchRecon en arrière-plan
start python twitchrecon.py

REM Lancer le Dashboard Flask
cd dashboard
python app.py