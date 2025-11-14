"""
Point d'entrée de l'application - Évite les imports circulaires
"""
import sys
import os

# Ajouter le dossier gestiostock au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'gestiostock'))

from gestiostock.app import create_app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        from gestiostock.app import init_database
        init_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)