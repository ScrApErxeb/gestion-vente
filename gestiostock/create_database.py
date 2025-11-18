from app import create_app
from models import db

def fix_relationships():
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Réparation des relations...")
            
            # Supprimer toutes les tables
            db.drop_all()
            print("✅ Tables supprimées")
            
            # Recréer avec les nouvelles relations
            db.create_all()
            print("✅ Tables recréées avec les relations corrigées")
            
            # Vérifier
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables disponibles: {len(tables)}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_relationships()