#!/usr/bin/env python3
"""
GestioStock - Point d'entrée principal de l'application
"""

import os
from flask import Flask, render_template, jsonify, redirect, url_for, session, request, flash
from flask_login import LoginManager, login_required
from flask_cors import CORS
from config import Config
from models import db, User

from utils.demo_data import init_demo_data


# -------------------------
# Fonction pour enregistrer les blueprints
# -------------------------
def register_blueprints(app):
    """Enregistre tous les blueprints de l'application"""
    try:
        # Importer les blueprints
        from routes.auth import auth_bp
        from routes.clients import clients_bp
        from routes.produits import produits_bp
        from routes.ventes import ventes_bp
        from routes.fournisseurs import fournisseurs_bp
        from routes.commandes import commandes_bp
        from routes.statistiques import statistiques_bp
        from routes.api import api_bp
        from routes.exporter import exporter_bp
        from routes.depenses import depenses_bp

        # Enregistrer les blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(clients_bp)
        app.register_blueprint(produits_bp)
        app.register_blueprint(ventes_bp)
        app.register_blueprint(fournisseurs_bp)
        app.register_blueprint(commandes_bp)
        app.register_blueprint(statistiques_bp)
        app.register_blueprint(exporter_bp, url_prefix='/exporter')
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(depenses_bp)

        print("✅ Tous les blueprints ont été enregistrés avec succès !")

    except ImportError as e:
        print(f"❌ Erreur lors de l'import des blueprints : {e}")
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement des blueprints : {e}")


# -------------------------
# Création de l'application Flask
# -------------------------
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)

    # Configuration Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Empêche Flask-Login de renvoyer du HTML pour les requêtes AJAX.
        """
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Authentification requise"}), 401
        return redirect(url_for(login_manager.login_view))


    # Blueprints
    register_blueprints(app)

    # CORS
    CORS(app,
         supports_credentials=True,
         origins=["http://localhost:5000", "http://127.0.0.1:5000"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # -------------------------
    # ROUTES PRINCIPALES
    # -------------------------
    @app.route('/')
    @login_required
    def index():
        return render_template('dashboard.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/parametres')
    @login_required
    def parametres_page():
        return render_template('parametres.html')

    # -------------------------
    # API DASHBOARD
    # -------------------------
    @app.route('/api/dashboard')
    @login_required
    def api_dashboard():
        try:
            stats = {
                'devise': 'F CFA',
                'ventes': {
                    'jour': 125000,
                    'mois': 1850000,
                    'annee': 22450000,
                    'mensuelles': [
                        {'mois': 'Jan', 'montant': 1200000},
                        {'mois': 'Fév', 'montant': 1500000},
                        {'mois': 'Mar', 'montant': 1800000},
                        {'mois': 'Avr', 'montant': 1650000},
                        {'mois': 'Mai', 'montant': 1900000},
                        {'mois': 'Jun', 'montant': 2100000},
                        {'mois': 'Jul', 'montant': 1950000},
                        {'mois': 'Aoû', 'montant': 1850000},
                        {'mois': 'Sep', 'montant': 2000000},
                        {'mois': 'Oct', 'montant': 2200000},
                        {'mois': 'Nov', 'montant': 2350000},
                        {'mois': 'Déc', 'montant': 1850000}
                    ]
                },
                'stats_globales': {
                    'categories': 8,
                    'fournisseurs': 12
                },
                'produits': {
                    'total': 156,
                    'stock_faible': 7,
                    'top_ventes': [
                        {'nom': 'Smartphone X10', 'quantite': 45, 'ca': 2250000},
                        {'nom': 'Ecouteurs Pro', 'quantite': 38, 'ca': 950000},
                        {'nom': 'Chargeur Rapide', 'quantite': 32, 'ca': 320000},
                        {'nom': 'Tablette Mini', 'quantite': 28, 'ca': 1960000},
                        {'nom': 'Powerbank 20000mAh', 'quantite': 25, 'ca': 625000},
                        {'nom': 'Câble USB-C', 'quantite': 22, 'ca': 110000},
                        {'nom': 'Haut-parleur Bluetooth', 'quantite': 18, 'ca': 720000}
                    ]
                },
                'clients': {
                    'total': 124,
                    'nouveaux': 8
                },
                'commandes': {
                    'en_cours': 5,
                    'montant_en_cours': 750000
                }
            }
            
            return jsonify(stats)
            
        except Exception as e:
            print(f"Erreur API dashboard: {e}")
            return jsonify({'error': str(e)}), 500

    print(app.url_map)

    # Debug helper: list registered endpoints when in debug mode
    if app.config.get('DEBUG', False):
        @app.route('/__debug/routes')
        def debug_routes():
            # Return a simple list of endpoint names and their rules to help local debugging
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append({'rule': str(rule), 'endpoint': rule.endpoint, 'methods': sorted(list(rule.methods))})
            from flask import jsonify
            return jsonify(sorted(routes, key=lambda r: r['endpoint']))

    # -------------------------
    # GESTION D'ERREURS
    # -------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    # Middleware pour cookies
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    return app


# -------------------------
# Initialisation DB
# -------------------------
def init_database(app):
    with app.app_context():
        db.create_all()
        if User.query.first() is None:
            init_demo_data()
            print("✅ Base de données initialisée avec succès!")
            print("👤 Admin: admin / admin123")
            print("👤 Vendeur: vendeur / vendeur123")


# -------------------------
# Fonction principale
# -------------------------
def main():
    print("🚀 Démarrage de GestioStock...")

    app = create_app()
    init_database(app)

    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    url = f"http://{host}:{port}"

    import webbrowser
    import threading

    def ouvrir_navigateur():
        webbrowser.open(url)

    threading.Timer(1.5, ouvrir_navigateur).start()

    print(f"📍 URL: {url}")
    print("⏹️  Ctrl+C pour arrêter le serveur")

    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    main()
