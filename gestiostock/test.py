#!/usr/bin/env python3
from flask import Flask

# Création de l'application Flask
app = Flask(__name__)

# Routes de test
@app.route('/')
def index():
    return "🚀 Serveur Flask fonctionne !"

@app.route('/dashboard')
def dashboard():
    return "📊 Tableau de bord"

@app.route('/test')
def test():
    return "✅ Route de test OK"

# Fonction principale
if __name__ == '__main__':
    print("🚀 Démarrage du serveur Flask de test...")
    app.run(host='127.0.0.1', port=5000, debug=True)
