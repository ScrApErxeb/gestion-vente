#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, LoginManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -------------------------
# Fonction pour enregistrer les blueprints
# -------------------------
def register_blueprints(app):
    """Enregistre tous les blueprints de l'application"""
    try:
        from routes.auth import auth_bp
        from routes.clients import clients_bp
        from routes.produits import produits_bp
        from routes.ventes import ventes_bp
        from routes.fournisseurs import fournisseurs_bp
        from routes.commandes import commandes_bp
        from routes.statistiques import statistiques_bp
        from routes.api import api_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(clients_bp)
        app.register_blueprint(produits_bp)
        app.register_blueprint(ventes_bp)
        app.register_blueprint(fournisseurs_bp)
        app.register_blueprint(commandes_bp)
        app.register_blueprint(statistiques_bp)
        app.register_blueprint(api_bp, url_prefix='/api')

        print("✅ Tous les blueprints ont été enregistrés avec succès !")

    except ImportError as e:
        print(f"❌ Erreur lors de l'import des blueprints : {e}")
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement des blueprints : {e}")

# -------------------------
# Création de l'application
# -------------------------
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gestiostock.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    from models import db, User
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Enregistrement des blueprints
    register_blueprints(app)

    # Routes de test / dashboard
    @app.route('/')
    def index():
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    return app

# -------------------------
# Fonction principale
# -------------------------
def main():
    app = create_app()
    with app.app_context():
        from models import db
        db.create_all()

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug, use_reloader=True)

if __name__ == '__main__':
    main()
