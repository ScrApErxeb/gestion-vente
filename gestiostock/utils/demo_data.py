from models import db, User, Categorie, Produit, Fournisseur, Client, ParametreSysteme
from datetime import datetime

def init_demo_data():
    """Initialise la base de données avec des données de démonstration"""
    
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
    
    # Catégories
    cat_elec = Categorie(nom="Électronique", description="Appareils électroniques et accessoires")
    cat_vete = Categorie(nom="Vêtements", description="Articles vestimentaires")
    cat_alim = Categorie(nom="Alimentation", description="Produits alimentaires")
    db.session.add_all([cat_elec, cat_vete, cat_alim])
    db.session.commit()
    
    # Fournisseurs
    f1 = Fournisseur(
        nom="TechSupply Burkina",
        contact="Ibrahim Sawadogo",
        telephone="70123456",
        email="contact@techsupply.bf",
        adresse="Zone industrielle Kossodo",
        ville="Ouagadougou",
        conditions_paiement="30 jours",
        delai_livraison=7
    )
    f2 = Fournisseur(
        nom="Mode & Style",
        contact="Aminata Ouédraogo",
        telephone="75654321",
        email="info@modestyle.bf",
        adresse="Avenue Kwamé N'Krumah",
        ville="Ouagadougou",
        conditions_paiement="Comptant",
        delai_livraison=3
    )
    db.session.add_all([f1, f2])
    db.session.commit()
    
    # Produits
    p1 = Produit(
        nom="Ordinateur Portable HP",
        reference="ORD-HP-001",
        code_barre="3760123456789",
        description="HP 15.6\" Intel Core i5, 8GB RAM, 256GB SSD",
        prix_achat=350000,
        prix_vente=450000,
        tva=0,
        stock_actuel=12,
        stock_min=3,
        stock_max=30,
        categorie_id=cat_elec.id,
        fournisseur_id=f1.id,
        unite_mesure="unité",
        emplacement="Rayon A-1"
    )
    
    p2 = Produit(
        nom="Smartphone Samsung Galaxy A54",
        reference="TEL-SAM-A54",
        code_barre="8806094123456",
        description="6.4\" AMOLED, 128GB, Triple caméra",
        prix_achat=180000,
        prix_vente=250000,
        tva=0,
        stock_actuel=25,
        stock_min=5,
        stock_max=50,
        categorie_id=cat_elec.id,
        fournisseur_id=f1.id,
        unite_mesure="unité",
        emplacement="Rayon A-2"
    )
    
    db.session.add_all([p1, p2])
    db.session.commit()
    
    # Clients
    c1 = Client(
        nom="Ouédraogo",
        prenom="Jean",
        email="jean.ouedraogo@example.com",
        telephone="70123456",
        adresse="Secteur 15, Ouaga 2000",
        ville="Ouagadougou",
        type_client="particulier"
    )
    
    db.session.add(c1)
    db.session.commit()
    
    # Paramètres système
    params = [
        ParametreSysteme(cle='nom_entreprise', valeur='GestioStock SARL', description='Nom de l\'entreprise'),
        ParametreSysteme(cle='adresse_entreprise', valeur='Ouagadougou, Burkina Faso', description='Adresse'),
        ParametreSysteme(cle='telephone_entreprise', valeur='70000000', description='Téléphone'),
        ParametreSysteme(cle='email_entreprise', valeur='contact@gestiostock.bf', description='Email'),
    ]
    
    for param in params:
        db.session.add(param)
    
    db.session.commit()