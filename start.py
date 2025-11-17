#!/usr/bin/env python3
"""
Script de démarrage simplifié pour GestioStock PRO - Windows
"""
import os
import sys
import webbrowser
import time
import subprocess
from datetime import datetime

def log_message(message):
    """Affiche un message avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_python():
    """Vérifie que Python est accessible"""
    try:
        import sys
        log_message(f"✅ Python {sys.version.split()[0]} détecté")
        return True
    except Exception as e:
        log_message(f"❌ Erreur Python: {e}")
        return False

def check_venv():
    """Vérifie et active l'environnement virtuel"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        log_message("✅ Environnement virtuel activé")
        return True
    else:
        log_message("⚠️  Environnement virtuel non activé")
        # Essayer d'activer venv
        if os.path.exists("venv"):
            venv_script = "venv\\Scripts\\activate_this.py"
            if os.path.exists(venv_script):
                try:
                    with open(venv_script) as f:
                        exec(f.read(), {'__file__': venv_script})
                    log_message("✅ Environnement virtuel activé")
                    return True
                except Exception as e:
                    log_message(f"❌ Erreur activation venv: {e}")
        return False

def install_requirements():
    """Installe les dépendances si besoin"""
    if os.path.exists("requirements.txt"):
        log_message("📦 Vérification des dépendances...")
        try:
            import flask
            log_message("✅ Dépendances déjà installées")
        except ImportError:
            log_message("🔧 Installation des dépendances...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                log_message("✅ Dépendances installées avec succès")
            except subprocess.CalledProcessError as e:
                log_message(f"❌ Erreur installation dépendances: {e}")
                return False
    return True

def start_application():
    """Démarre l'application Flask"""
    log_message("🚀 Démarrage de GestioStock PRO...")
    
    try:
        # Vérifications préalables
        if not check_python():
            return False
            
        if not check_venv():
            log_message("⚠️  Continuation sans environnement virtuel")
            
        if not install_requirements():
            return False
        
        # Importer l'application Flask
        log_message("📁 Chargement de l'application...")
        
        # Ajouter le chemin courant
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        try:
            from gestiostock.app import create_app, init_database
        except ImportError as e:
            log_message(f"❌ Erreur importation: {e}")
            log_message("💡 Vérifiez la structure des dossiers")
            return False
        
        # Créer et configurer l'application
        app = create_app()
        
        # Initialiser la base de données
        log_message("🗃️ Initialisation de la base de données...")
        with app.app_context():
            init_database()
        log_message("✅ Base de données prête")
        
        # Ouvrir le navigateur après un délai
        log_message("🌐 Démarrage du serveur...")
        log_message("📍 L'application sera disponible sur: http://localhost:5000")
        
        # Ouvrir le navigateur dans 3 secondes
        def open_browser():
            time.sleep(3)
            log_message("📊 Ouverture du navigateur...")
            webbrowser.open("http://localhost:5000")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Démarrer le serveur Flask
        log_message("🎉 Application démarrée!")
        log_message("🔐 Comptes: admin/admin123 ou vendeur/vendeur123")
        log_message("💡 Utilisez Ctrl+C pour arrêter l'application")
        print("-" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
        
        return True
        
    except KeyboardInterrupt:
        log_message("👋 Arrêt de l'application...")
        return True
    except Exception as e:
        log_message(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 GESTIOSTOCK PRO - LANCEUR AUTOMATIQUE")
    print("=" * 60)
    
    success = start_application()
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ Le démarrage a échoué")
        print("🔧 Solutions possibles:")
        print("   1. Vérifiez que Python 3.8+ est installé")
        print("   2. Exécutez: python -m venv venv")
        print("   3. Puis: venv\\Scripts\\activate")
        print("   4. Enfin: pip install -r requirements.txt")
        print("=" * 60)
        input("Appuyez sur Entrée pour quitter...")