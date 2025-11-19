from app import create_app
from models import db, User, Categorie, Produit, Client, Fournisseur, ParametreSysteme
from datetime import datetime

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        try:
            print("📝 Création des données de démonstration...")
            
            # === PARAMÈTRES SYSTÈME ===
            parametres = [
                ParametreSysteme(
                    cle='nom_entreprise', 
                    valeur='GestiStock Burkina', 
                    description='Nom de l\'entreprise'
                ),
                ParametreSysteme(
                    cle='devise_par_defaut', 
                    valeur='XOF', 
                    description='Devise par défaut'
                ),
                ParametreSysteme(
                    cle='tva_par_defaut', 
                    valeur='18', 
                    description='TVA par défaut (%)', 
                    type_valeur='number'
                ),
                ParametreSysteme(
                    cle='pays_par_defaut', 
                    valeur='Burkina Faso', 
                    description='Pays par défaut'
                ),
                ParametreSysteme(
                    cle='seuil_stock_faible', 
                    valeur='5', 
                    description='Seuil de stock faible', 
                    type_valeur='number'
                ),
            ]
            
            for param in parametres:
                db.session.add(param)
            
            # === UTILISATEURS ===
            admin = User(
                username='admin',
                email='admin@gestiostock.bf',
                nom='Admin',
                prenom='System',
                role='admin',
                telephone='+226 70 000 000'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            manager = User(
                username='manager',
                email='manager@gestiostock.bf',
                nom='Diallo',
                prenom='Fatou',
                role='manager',
                telephone='+226 70 111 111'
            )
            manager.set_password('manager123')
            db.session.add(manager)
            
            vendeur = User(
                username='vendeur',
                email='vendeur@gestiostock.bf',
                nom='Traoré',
                prenom='Jean',
                role='user',
                telephone='+226 70 222 222'
            )
            vendeur.set_password('vendeur123')
            db.session.add(vendeur)
            
            # === CATÉGORIES ===
            categories = [
                Categorie(nom='Électronique', description='Appareils électroniques et gadgets'),
                Categorie(nom='Informatique', description='Ordinateurs, périphériques et accessoires'),
                Categorie(nom='Téléphonie', description='Smartphones, tablettes et accessoires'),
                Categorie(nom='Bureau', description='Fournitures de bureau'),
                Categorie(nom='Réseau', description='Équipements réseau et communication'),
            ]
            
            for cat in categories:
                db.session.add(cat)
            
            db.session.flush()  # Pour obtenir les IDs
            
            # === FOURNISSEURS ===
            fournisseurs = [
                Fournisseur(
                    nom='TechDistrib Burkina', 
                    contact='M. Kaboré',
                    email='contact@techdistrib.bf', 
                    telephone='+226 70 123 456',
                    adresse='Avenue Kwame Nkrumah, Ouagadougou',
                    ville='Ouagadougou',
                    conditions_paiement='30 jours net'
                ),
                Fournisseur(
                    nom='OfficePro SA', 
                    contact='Mme. Ouédraogo',
                    email='info@officepro.bf', 
                    telephone='+226 70 654 321',
                    adresse='Rue de la Commerce, Bobo-Dioulasso',
                    ville='Bobo-Dioulasso',
                    conditions_paiement='15 jours net'
                ),
                Fournisseur(
                    nom='ElectroImport', 
                    contact='M. Sawadogo',
                    email='contact@electroimport.bf', 
                    telephone='+226 70 789 012',
                    adresse='Zone industrielle, Koudougou',
                    ville='Koudougou',
                    conditions_paiement='Paiement comptant'
                ),
            ]
            
            for fourn in fournisseurs:
                db.session.add(fourn)
            
            db.session.flush()
            
            # === CLIENTS ===
            clients = [
                Client(
                    nom='Konaté', 
                    prenom='Moussa', 
                    entreprise='Entreprise K SARL',
                    email='moussa@entreprisek.bf',
                    telephone='+226 70 111 222',
                    adresse='Secteur 15, Ouagadougou',
                    ville='Ouagadougou',
                    type_client='professionnel',
                    remise_defaut=5.0
                ),
                Client(
                    nom='Traoré', 
                    prenom='Aïcha', 
                    email='aicha.traore@email.com',
                    telephone='+226 70 333 444',
                    adresse='Dapoya, Ouagadougou',
                    ville='Ouagadougou',
                    type_client='particulier'
                ),
                Client(
                    nom='CompuTech', 
                    entreprise='CompuTech Burkina',
                    email='contact@computeck.bf',
                    telephone='+226 70 555 666',
                    adresse='Av. de la Nation, Bobo-Dioulasso',
                    ville='Bobo-Dioulasso',
                    type_client='professionnel',
                    remise_defaut=10.0
                ),
                Client(
                    nom='Sawadogo',
                    prenom='Boubacar',
                    email='boubacar.s@email.com',
                    telephone='+226 70 777 888',
                    adresse='Gounghin, Ouagadougou',
                    ville='Ouagadougou',
                    type_client='particulier'
                )
            ]
            
            for client in clients:
                db.session.add(client)
            
            db.session.flush()
            
            # === PRODUITS ===
            produits = [
                Produit(
                    nom='Laptop Dell Inspiron 15',
                    reference='DEL-INSP-15-001',
                    code_barre='1234567890123',
                    description='Laptop Dell Inspiron 15 pouces, 8GB RAM, 256GB SSD, Intel i5',
                    prix_achat=450000,
                    prix_vente=550000,
                    tva=18.0,
                    stock_actuel=8,
                    stock_min=2,
                    stock_max=20,
                    categorie_id=categories[1].id,  # Informatique
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon A1'
                ),
                Produit(
                    nom='Smartphone Samsung Galaxy A54',
                    reference='SAM-A54-001',
                    code_barre='1234567890124',
                    description='Smartphone Samsung Galaxy A54 128GB Dual SIM, 5G',
                    prix_achat=175000,
                    prix_vente=220000,
                    tva=18.0,
                    stock_actuel=15,
                    stock_min=5,
                    stock_max=50,
                    categorie_id=categories[2].id,  # Téléphonie
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon B2'
                ),
                Produit(
                    nom='Souris Sans Fil Logitech M170',
                    reference='LOG-MOUS-001',
                    code_barre='1234567890125',
                    description='Souris sans fil Logitech M170, USB, 12 mois autonomie',
                    prix_achat=7500,
                    prix_vente=12000,
                    tva=18.0,
                    stock_actuel=45,
                    stock_min=10,
                    stock_max=100,
                    categorie_id=categories[1].id,  # Informatique
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='unité',
                    emplacement='Rayon C3'
                ),
                Produit(
                    nom='Câble HDMI 2m Haute Vitesse',
                    reference='CAB-HDMI-002',
                    code_barre='1234567890126',
                    description='Câble HDMI 2.0 haute vitesse 2 mètres, 4K',
                    prix_achat=2500,
                    prix_vente=5000,
                    tva=18.0,
                    stock_actuel=80,
                    stock_min=20,
                    stock_max=200,
                    categorie_id=categories[0].id,  # Électronique
                    fournisseur_id=fournisseurs[2].id,
                    unite_mesure='unité',
                    emplacement='Rayon D4'
                ),
                Produit(
                    nom='Clé USB 64GB USB 3.0',
                    reference='USB-64G-001',
                    code_barre='1234567890127',
                    description='Clé USB 3.0 64GB, transfert jusquà 100MB/s',
                    prix_achat=8000,
                    prix_vente=15000,
                    tva=18.0,
                    stock_actuel=25,
                    stock_min=5,
                    stock_max=100,
                    categorie_id=categories[1].id,  # Informatique
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='unité',
                    emplacement='Rayon C5'
                ),
                Produit(
                    nom='Imprimante HP LaserJet Pro',
                    reference='HP-LASER-001',
                    code_barre='1234567890128',
                    description='Imprimante laser HP LaserJet Pro M15w, WiFi',
                    prix_achat=120000,
                    prix_vente=155000,
                    tva=18.0,
                    stock_actuel=3,
                    stock_min=1,
                    stock_max=10,
                    categorie_id=categories[1].id,  # Informatique
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon A2'
                ),
                Produit(
                    nom='Cartouche Encre HP 304',
                    reference='HP-ENC-304',
                    code_barre='1234567890129',
                    description='Cartouche d\'encre noire HP 304 originale',
                    prix_achat=15000,
                    prix_vente=22000,
                    tva=18.0,
                    stock_actuel=12,
                    stock_min=5,
                    stock_max=50,
                    categorie_id=categories[3].id,  # Bureau
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='unité',
                    emplacement='Rayon E1'
                ),
                Produit(
                    nom='Routeur WiFi TP-Link Archer',
                    reference='TPL-ARCH-001',
                    code_barre='1234567890130',
                    description='Routeur WiFi TP-Link Archer C6, Dual Band, 1200Mbps',
                    prix_achat=35000,
                    prix_vente=48000,
                    tva=18.0,
                    stock_actuel=6,
                    stock_min=2,
                    stock_max=20,
                    categorie_id=categories[4].id,  # Réseau
                    fournisseur_id=fournisseurs[2].id,
                    unite_mesure='unité',
                    emplacement='Rayon F2'
                )
            ]
            
            for produit in produits:
                db.session.add(produit)
            
            # === VALIDATION FINALE ===
            db.session.commit()
            
            print("✅ Données de démonstration créées avec succès!")
            print("\n📋 RÉCAPITULATIF:")
            print(f"   👤 Utilisateurs: 3 (admin, manager, vendeur)")
            print(f"   📁 Catégories: {len(categories)}")
            print(f"   🏢 Fournisseurs: {len(fournisseurs)}")
            print(f"   👥 Clients: {len(clients)}")
            print(f"   📦 Produits: {len(produits)}")
            print(f"   ⚙️  Paramètres: {len(parametres)}")
            
            print("\n🔐 COMPTES DE TEST:")
            print("   Administrateur: username=admin, password=admin123")
            print("   Manager: username=manager, password=manager123")
            print("   Vendeur: username=vendeur, password=vendeur123")
            
            print("\n📍 PRODUITS EN STOCK FAIBLE:")
            produits_faible = [p for p in produits if p.stock_actuel <= p.stock_min]
            for pf in produits_faible:
                print(f"   ⚠️  {pf.nom}: {pf.stock_actuel} unités (min: {pf.stock_min})")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création des données: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_sample_data()