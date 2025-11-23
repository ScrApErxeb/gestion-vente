

from models import db, User, Categorie, Produit, Fournisseur, Client, ParametreSysteme


def init_run():


        # Créer utilisateur admin
    admin = User(
        username='admin',
        email='admin@gestiostock.com',
        nom='Admin',
        prenom='GestioStock',
        role='admin',
        telephone='70000000'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Créer utilisateur standard
    user = User(
        username='vendeur',
        email='vendeur@gestiostock.com',
        nom='Sawadogo',
        prenom='Marie',
        role='user',
        telephone='70111111'
    )
    user.set_password('vendeur123')
    db.session.add(user)
    
    db.session.commit()