from app import create_app
from models import db

def safe_migration():
    app = create_app()
    
    with app.app_context():
        # D'abord, supprimer tous les index problématiques
        from sqlalchemy import text
        
        try:
            # Liste des index à vérifier/supprimer
            problematic_indexes = [
                'idx_vente_item_reference',
                'idx_vente_items_reference'
            ]
            
            for index_name in problematic_indexes:
                db.session.execute(text(f'DROP INDEX IF EXISTS {index_name}'))
            
            db.session.commit()
            print("✅ Index problématiques supprimés")
            
            # Maintenant créer les bons index
            db.create_all()
            print("✅ Modèles recréés avec les bons index")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            db.session.rollback()

if __name__ == '__main__':
    safe_migration()