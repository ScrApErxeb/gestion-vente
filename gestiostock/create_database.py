#!/usr/bin/env python3
"""
Script de réinitialisation de la base de données
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, app_context
from models import db

def reset_database():
    """Réinitialise complètement la base de données"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Réinitialisation de la base de données...")
            
            # Supprimer toutes les tables
            db.drop_all()
            print("✅ Tables supprimées")
            
            # Recréer les tables
            db.create_all()
            print("✅ Tables recréées")
            
            # Vérifier la structure
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("📊 Structure de la base:")
            for table in sorted(tables):
                columns = [col['name'] for col in inspector.get_columns(table)]
                print(f"   📦 {table}: {len(columns)} colonnes")
            
            print("🎉 Base de données réinitialisée avec succès!")
            print("\n💡 Exécutez 'python seed.py' pour créer les données de démonstration")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    confirm = input("⚠️  Êtes-vous sûr de vouloir réinitialiser la base de données? (yes/no): ")
    if confirm.lower() in ['yes', 'y', 'oui', 'o']:
        success = reset_database()
        if success:
            print("✅ Réinitialisation terminée avec succès!")
        else:
            print("❌ Réinitialisation échouée!")
            sys.exit(1)
    else:
        print("❌ Opération annulée")