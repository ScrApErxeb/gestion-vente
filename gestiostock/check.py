from app import create_app
from models import db

def check_database():
    app = create_app()
    
    with app.app_context():
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("🔍 VÉRIFICATION DE LA BASE DE DONNÉES")
        print("=" * 50)
        
        for table in sorted(tables):
            print(f"\n📊 Table: {table}")
            columns = inspector.get_columns(table)
            print(f"   Colonnes: {len(columns)}")
            
            # Compter les enregistrements
            try:
                count = db.session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                print(f"   Enregistrements: {count}")
            except Exception as e:
                print(f"   Enregistrements: Erreur - {e}")

if __name__ == '__main__':
    check_database()