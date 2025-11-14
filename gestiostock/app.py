"""
GestioStock - Point d'entrée principal
"""
from flask import Flask, render_template, jsonify
from flask_login import LoginManager, login_required
from config import Config
from models import db, User

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
    
    # Import et enregistrement des Blueprints
    from routes.auth import auth_bp
    from routes.produits import produits_bp
    from routes.ventes import ventes_bp
    from routes.clients import clients_bp
    from routes.fournisseurs import fournisseurs_bp
    from routes.commandes import commandes_bp
    from routes.statistiques import statistiques_bp
    from routes.api import api_bp  # NOUVEAU
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(produits_bp)
    app.register_blueprint(ventes_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(fournisseurs_bp)
    app.register_blueprint(commandes_bp)
    app.register_blueprint(statistiques_bp)
    app.register_blueprint(api_bp)  # NOUVEAU
    
    # Routes de base
    @app.route('/')
    @login_required
    def index():
        return render_template('dashboard.html')
    
    @app.route('/parametres')
    @login_required
    def parametres_page():
        return render_template('parametres.html')
    
    # Gestion d'erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    return app

def init_database():
    """Initialise la base de données"""
    from utils.demo_data import init_demo_data
    
    # Création des tables


    db.create_all()
    
    # Vérifier si des données existent déjà
    if User.query.first() is None:
        init_demo_data()
        print("✅ Base de données initialisée avec succès!")
        print("👤 Admin: admin / admin123")
        print("👤 Vendeur: vendeur / vendeur123")

# Code d'exécution direct
if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        init_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)