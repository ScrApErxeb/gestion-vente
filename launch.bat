@echo off
:: -------------------------------
:: Lance GestioStock sur machine isolée
:: -------------------------------

:: Chemin vers le dossier courant
SET BASE_DIR=%~dp0
SET APP_DIR=%BASE_DIR%gestiostock

:: Installer les dépendances offline si besoin
python -m pip install --no-index --find-links=%BASE_DIR%packages -r %BASE_DIR%requirements.txt

:: Lancer le serveur Flask
cd %APP_DIR%
start "" http://127.0.0.1:5000
python app.py

pause
