from app import create_app
from models import db

def reset_database():
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Réinitialisation complète de la base de données...")
            
            # 1. Supprimer toutes les tables
            db.drop_all()
            print("✅ Tables supprimées")
            
            # 2. Recréer les tables avec les nouvelles relations
            db.create_all()
            print("✅ Tables recréées")
            
            # 3. Vérifier la structure
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("📊 Structure de la base:")
            for table in sorted(tables):
                columns = [col['name'] for col in inspector.get_columns(table)]
                print(f"   📦 {table}: {len(columns)} colonnes")
            
            print("🎉 Base de données réinitialisée avec succès!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    reset_database()