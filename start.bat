@echo off
chcp 65001 > nul
title GestioStock PRO - Démarrage

echo.
echo 🚀 Démarrage de GestioStock PRO...
echo.

:: Vérifier si Python est installé
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo 📥 Téléchargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo ❌ Environnement virtuel non trouvé
    echo 🔧 Création de l'environnement virtuel...
    python -m venv venv
)

:: Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

:: Installer les dépendances si requirements.txt existe
if exist "requirements.txt" (
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
)

:: Démarrer l'application
echo 🚀 Lancement de l'application...
python run.py

pause