#!/usr/bin/env python3
"""
Script d'initialisation des données de démonstration pour GestiStock
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Categorie, Produit, Client, Fournisseur, ParametreSysteme

def create_sample_data():
    """Crée les données de démonstration"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🌱 Création des données de démonstration...")
            
            # Vérifier si des données existent déjà
            if User.query.first():
                print("⚠️  Des données existent déjà. Utilisez 'python reset_database.py' pour réinitialiser.")
                return
            
            # === PARAMÈTRES SYSTÈME ===
            print("📋 Création des paramètres système...")
            parametres = [
                ParametreSysteme(
                    cle='nom_entreprise', 
                    valeur='GestiStock Burkina', 
                    description='Nom de l\'entreprise',
                    type_valeur='string'
                ),
                ParametreSysteme(
                    cle='devise_par_defaut', 
                    valeur='XOF', 
                    description='Devise par défaut',
                    type_valeur='string'
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
                    description='Pays par défaut',
                    type_valeur='string'
                ),
                ParametreSysteme(
                    cle='seuil_stock_faible', 
                    valeur='5', 
                    description='Seuil de stock faible',
                    type_valeur='number'
                ),
                ParametreSysteme(
                    cle='email_contact', 
                    valeur='contact@gestiostock.bf', 
                    description='Email de contact',
                    type_valeur='string'
                ),
                ParametreSysteme(
                    cle='telephone_contact', 
                    valeur='+226 25 30 12 34', 
                    description='Téléphone de contact',
                    type_valeur='string'
                ),
            ]
            
            for param in parametres:
                db.session.add(param)
            
            db.session.flush()
            print(f"✅ {len(parametres)} paramètres système créés")
            
            # === UTILISATEURS ===
            print("👤 Création des utilisateurs...")
            users = [
                User(
                    username='admin',
                    email='admin@gestiostock.bf',
                    nom='Admin',
                    prenom='System',
                    role='admin',
                    telephone='+226 70 000 000',
                    actif=True
                ),
                User(
                    username='manager',
                    email='manager@gestiostock.bf',
                    nom='Diallo',
                    prenom='Fatou',
                    role='manager',
                    telephone='+226 70 111 111',
                    actif=True
                ),
                User(
                    username='vendeur',
                    email='vendeur@gestiostock.bf',
                    nom='Traoré',
                    prenom='Jean',
                    role='user',
                    telephone='+226 70 222 222',
                    actif=True
                ),
                User(
                    username='kone',
                    email='amadou.kone@gestiostock.bf',
                    nom='Koné',
                    prenom='Amadou',
                    role='user',
                    telephone='+226 70 333 333',
                    actif=True
                )
            ]
            
            # Définir les mots de passe
            users[0].set_password('admin123')
            users[1].set_password('manager123')
            users[2].set_password('vendeur123')
            users[3].set_password('kone123')
            
            for user in users:
                db.session.add(user)
            
            db.session.flush()
            print(f"✅ {len(users)} utilisateurs créés")
            
            # === CATÉGORIES ===
            print("📁 Création des catégories...")
            categories = [
                Categorie(
                    nom='Électronique',
                    description='Appareils électroniques et gadgets',
                    actif=True
                ),
                Categorie(
                    nom='Informatique', 
                    description='Ordinateurs, périphériques et accessoires',
                    actif=True
                ),
                Categorie(
                    nom='Téléphonie',
                    description='Smartphones, tablettes et accessoires',
                    actif=True
                ),
                Categorie(
                    nom='Bureau',
                    description='Fournitures de bureau',
                    actif=True
                ),
                Categorie(
                    nom='Réseau',
                    description='Équipements réseau et communication',
                    actif=True
                ),
                Categorie(
                    nom='Composants',
                    description='Composants électroniques',
                    actif=True
                )
            ]
            
            for cat in categories:
                db.session.add(cat)
            
            db.session.flush()
            print(f"✅ {len(categories)} catégories créées")
            
            # === FOURNISSEURS ===
            print("🏭 Création des fournisseurs...")
            fournisseurs = [
                Fournisseur(
                    nom='TechDistrib Burkina',
                    contact='M. Kaboré',
                    email='contact@techdistrib.bf',
                    telephone='+226 70 123 456',
                    telephone2='+226 25 40 12 34',
                    adresse='Avenue Kwame Nkrumah, Secteur 4',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    site_web='www.techdistrib.bf',
                    conditions_paiement='30 jours net',
                    delai_livraison=7,
                    devise_preferee='XOF',
                    notes='Fournisseur principal pour matériel informatique',
                    actif=True
                ),
                Fournisseur(
                    nom='OfficePro SA',
                    contact='Mme. Ouédraogo',
                    email='info@officepro.bf',
                    telephone='+226 70 654 321',
                    adresse='Rue de la Commerce, Zone Industrielle',
                    ville='Bobo-Dioulasso',
                    pays='Burkina Faso',
                    conditions_paiement='15 jours net',
                    delai_livraison=5,
                    devise_preferee='XOF',
                    notes='Spécialiste fournitures de bureau',
                    actif=True
                ),
                Fournisseur(
                    nom='ElectroImport',
                    contact='M. Sawadogo',
                    email='contact@electroimport.bf',
                    telephone='+226 70 789 012',
                    telephone2='+226 25 45 67 89',
                    adresse='Zone industrielle, Lot 45',
                    ville='Koudougou',
                    pays='Burkina Faso',
                    conditions_paiement='Paiement comptant',
                    delai_livraison=3,
                    devise_preferee='XOF',
                    notes='Importateur matériel électronique',
                    actif=True
                ),
                Fournisseur(
                    nom='MobileTech',
                    contact='M. Cissé',
                    email='ventes@mobiletech.bf',
                    telephone='+226 70 555 666',
                    adresse='Boulevard de la Révolution',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    conditions_paiement='30 jours net',
                    delai_livraison=10,
                    devise_preferee='XOF',
                    notes='Grossiste smartphones et tablettes',
                    actif=True
                )
            ]
            
            for fourn in fournisseurs:
                db.session.add(fourn)
            
            db.session.flush()
            print(f"✅ {len(fournisseurs)} fournisseurs créés")
            
            # === CLIENTS ===
            print("👥 Création des clients...")
            clients = [
                Client(
                    nom='Konaté',
                    prenom='Moussa',
                    entreprise='Entreprise K SARL',
                    email='moussa@entreprisek.bf',
                    telephone='+226 70 111 222',
                    adresse='Secteur 15, Rue 12.44',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    type_client='professionnel',
                    remise_defaut=5.0,
                    plafond_credit=500000,
                    devise_preferee='XOF',
                    notes='Client fidèle depuis 2020',
                    actif=True
                ),
                Client(
                    nom='Traoré',
                    prenom='Aïcha',
                    email='aicha.traore@email.com',
                    telephone='+226 70 333 444',
                    adresse='Dapoya, Rue du Marché',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    type_client='particulier',
                    remise_defaut=0.0,
                    plafond_credit=0,
                    devise_preferee='XOF',
                    actif=True
                ),
                Client(
                    nom='CompuTech',
                    entreprise='CompuTech Burkina',
                    email='contact@computeck.bf',
                    telephone='+226 70 555 666',
                    telephone2='+226 25 30 40 50',
                    adresse='Av. de la Nation, Immeuble SIAO',
                    ville='Bobo-Dioulasso',
                    pays='Burkina Faso',
                    type_client='professionnel',
                    remise_defaut=10.0,
                    plafond_credit=1000000,
                    devise_preferee='XOF',
                    notes='Revendeur informatique',
                    actif=True
                ),
                Client(
                    nom='Sawadogo',
                    prenom='Boubacar',
                    email='boubacar.s@email.com',
                    telephone='+226 70 777 888',
                    adresse='Gounghin, Avenue Yennenga',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    type_client='particulier',
                    remise_defaut=2.5,
                    plafond_credit=100000,
                    devise_preferee='XOF',
                    actif=True
                ),
                Client(
                    nom='Ministère TIC',
                    entreprise='Ministère des Technologies',
                    email='tic@gouv.bf',
                    telephone='+226 25 30 11 22',
                    adresse='Gouvernement, Koulouba',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    type_client='professionnel',
                    remise_defaut=15.0,
                    plafond_credit=2000000,
                    devise_preferee='XOF',
                    notes='Client institutionnel',
                    actif=True
                ),
                Client(
                    nom='Université',
                    entreprise='Université Joseph Ki-Zerbo',
                    email='achats@ujkz.bf',
                    telephone='+226 25 30 33 44',
                    adresse='Campus, 12 BP 417',
                    ville='Ouagadougou',
                    pays='Burkina Faso',
                    type_client='professionnel',
                    remise_defaut=12.0,
                    plafond_credit=1500000,
                    devise_preferee='XOF',
                    notes='Université publique',
                    actif=True
                )
            ]
            
            for client in clients:
                db.session.add(client)
            
            db.session.flush()
            print(f"✅ {len(clients)} clients créés")
            
            # === PRODUITS ===
            print("📦 Création des produits...")
            produits = [
                # Informatique
                Produit(
                    nom='Laptop Dell Inspiron 15',
                    reference='DEL-INSP-15-001',
                    code_barre='1234567890123',
                    description='Laptop Dell Inspiron 15 pouces, 8GB RAM, 256GB SSD, Intel i5-1135G7',
                    prix_achat=450000,
                    prix_vente=550000,
                    tva=18.0,
                    stock_actuel=8,
                    stock_min=2,
                    stock_max=20,
                    categorie_id=categories[1].id,
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon A1',
                    actif=True
                ),
                Produit(
                    nom='Souris Sans Fil Logitech M170',
                    reference='LOG-MOUS-001',
                    code_barre='1234567890125',
                    description='Souris sans fil Logitech M170, USB, 12 mois autonomie, 1000 DPI',
                    prix_achat=7500,
                    prix_vente=12000,
                    tva=18.0,
                    stock_actuel=45,
                    stock_min=10,
                    stock_max=100,
                    categorie_id=categories[1].id,
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='unité',
                    emplacement='Rayon C3',
                    actif=True
                ),
                Produit(
                    nom='Clé USB 64GB USB 3.0',
                    reference='USB-64G-001',
                    code_barre='1234567890127',
                    description='Clé USB 3.0 64GB, transfert jusquà 100MB/s, garantie 3 ans',
                    prix_achat=8000,
                    prix_vente=15000,
                    tva=18.0,
                    stock_actuel=25,
                    stock_min=5,
                    stock_max=100,
                    categorie_id=categories[1].id,
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='unité',
                    emplacement='Rayon C5',
                    actif=True
                ),
                Produit(
                    nom='Imprimante HP LaserJet Pro M15w',
                    reference='HP-LASER-001',
                    code_barre='1234567890128',
                    description='Imprimante laser HP LaserJet Pro M15w, WiFi, USB, impression mobile',
                    prix_achat=120000,
                    prix_vente=155000,
                    tva=18.0,
                    stock_actuel=3,
                    stock_min=1,
                    stock_max=10,
                    categorie_id=categories[1].id,
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon A2',
                    actif=True
                ),
                
                # Téléphonie
                Produit(
                    nom='Smartphone Samsung Galaxy A54',
                    reference='SAM-A54-001',
                    code_barre='1234567890124',
                    description='Smartphone Samsung Galaxy A54 128GB Dual SIM, 5G, 6.4" Super AMOLED',
                    prix_achat=175000,
                    prix_vente=220000,
                    tva=18.0,
                    stock_actuel=15,
                    stock_min=5,
                    stock_max=50,
                    categorie_id=categories[2].id,
                    fournisseur_id=fournisseurs[3].id,
                    unite_mesure='unité',
                    emplacement='Rayon B2',
                    actif=True
                ),
                Produit(
                    nom='Smartphone Tecno Spark 10',
                    reference='TEC-SPK-010',
                    code_barre='1234567890135',
                    description='Tecno Spark 10, 128GB, 8GB RAM, Double SIM, 5000mAh',
                    prix_achat=85000,
                    prix_vente=115000,
                    tva=18.0,
                    stock_actuel=22,
                    stock_min=8,
                    stock_max=60,
                    categorie_id=categories[2].id,
                    fournisseur_id=fournisseurs[3].id,
                    unite_mesure='unité',
                    emplacement='Rayon B3',
                    actif=True
                ),
                
                # Électronique
                Produit(
                    nom='Câble HDMI 2m Haute Vitesse',
                    reference='CAB-HDMI-002',
                    code_barre='1234567890126',
                    description='Câble HDMI 2.0 haute vitesse 2 mètres, 4K@60Hz, Ethernet',
                    prix_achat=2500,
                    prix_vente=5000,
                    tva=18.0,
                    stock_actuel=80,
                    stock_min=20,
                    stock_max=200,
                    categorie_id=categories[0].id,
                    fournisseur_id=fournisseurs[2].id,
                    unite_mesure='unité',
                    emplacement='Rayon D4',
                    actif=True
                ),
                Produit(
                    nom='Adaptateur USB-C vers HDMI',
                    reference='ADP-USBC-HDMI',
                    code_barre='1234567890136',
                    description='Adaptateur USB-C vers HDMI 4K, compatible MacBook et Windows',
                    prix_achat=12000,
                    prix_vente=18000,
                    tva=18.0,
                    stock_actuel=12,
                    stock_min=5,
                    stock_max=50,
                    categorie_id=categories[0].id,
                    fournisseur_id=fournisseurs[2].id,
                    unite_mesure='unité',
                    emplacement='Rayon D5',
                    actif=True
                ),
                
                # Bureau
                Produit(
                    nom='Cartouche Encre HP 304 Noire',
                    reference='HP-ENC-304N',
                    code_barre='1234567890129',
                    description='Cartouche d\'encre noire HP 304 originale, rendement 120 pages',
                    prix_achat=15000,
                    prix_vente=22000,
                    tva=18.0,
                    stock_actuel=12,
                    stock_min=5,
                    stock_max=50,
                    categorie_id=categories[3].id,
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='unité',
                    emplacement='Rayon E1',
                    actif=True
                ),
                Produit(
                    nom='Ramette Papier A4 80g',
                    reference='PAP-A4-500',
                    code_barre='1234567890137',
                    description='Ramette de papier A4 80g, 500 feuilles, blancheur 100%',
                    prix_achat=2500,
                    prix_vente=4000,
                    tva=18.0,
                    stock_actuel=35,
                    stock_min=10,
                    stock_max=100,
                    categorie_id=categories[3].id,
                    fournisseur_id=fournisseurs[1].id,
                    unite_mesure='ramette',
                    emplacement='Rayon E2',
                    actif=True
                ),
                
                # Réseau
                Produit(
                    nom='Routeur WiFi TP-Link Archer C6',
                    reference='TPL-ARCH-C6',
                    code_barre='1234567890130',
                    description='Routeur WiFi TP-Link Archer C6, Dual Band, 1200Mbps, 4 antennes',
                    prix_achat=35000,
                    prix_vente=48000,
                    tva=18.0,
                    stock_actuel=6,
                    stock_min=2,
                    stock_max=20,
                    categorie_id=categories[4].id,
                    fournisseur_id=fournisseurs[2].id,
                    unite_mesure='unité',
                    emplacement='Rayon F2',
                    actif=True
                ),
                Produit(
                    nom='Switch Gigabit 8 Ports',
                    reference='SW-GIGA-8P',
                    code_barre='1234567890138',
                    description='Switch réseau Gigabit 8 ports, bureau, fanless',
                    prix_achat=18000,
                    prix_vente=28000,
                    tva=18.0,
                    stock_actuel=8,
                    stock_min=3,
                    stock_max=25,
                    categorie_id=categories[4].id,
                    fournisseur_id=fournisseurs[2].id,
                    unite_mesure='unité',
                    emplacement='Rayon F3',
                    actif=True
                ),
                
                # Composants
                Produit(
                    nom='Disque Dur SSD 500GB',
                    reference='SSD-500G-SATA',
                    code_barre='1234567890139',
                    description='SSD 500GB SATA III, 2.5", lecture 550MB/s, écriture 500MB/s',
                    prix_achat=30000,
                    prix_vente=42000,
                    tva=18.0,
                    stock_actuel=10,
                    stock_min=3,
                    stock_max=30,
                    categorie_id=categories[5].id,
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon G1',
                    actif=True
                ),
                Produit(
                    nom='Mémoire RAM DDR4 8GB',
                    reference='RAM-DDR4-8G',
                    code_barre='1234567890140',
                    description='Mémoire RAM DDR4 8GB 2666MHz, PC4-21300, CL19',
                    prix_achat=18000,
                    prix_vente=25000,
                    tva=18.0,
                    stock_actuel=15,
                    stock_min=5,
                    stock_max=40,
                    categorie_id=categories[5].id,
                    fournisseur_id=fournisseurs[0].id,
                    unite_mesure='unité',
                    emplacement='Rayon G2',
                    actif=True
                )
            ]
            
            for produit in produits:
                db.session.add(produit)
            
            db.session.flush()
            print(f"✅ {len(produits)} produits créés")
            
            # === VALIDATION FINALE ===
            db.session.commit()
            
            # === AFFICHAGE RÉCAPITULATIF ===
            print("\n" + "="*60)
            print("🎉 DONNÉES DE DÉMONSTRATION CRÉÉES AVEC SUCCÈS!")
            print("="*60)
            print(f"📋 RÉCAPITULATIF:")
            print(f"   👤 Utilisateurs: {len(users)}")
            print(f"   📁 Catégories: {len(categories)}")
            print(f"   🏢 Fournisseurs: {len(fournisseurs)}")
            print(f"   👥 Clients: {len(clients)}")
            print(f"   📦 Produits: {len(produits)}")
            print(f"   ⚙️  Paramètres: {len(parametres)}")
            
            print("\n🔐 COMPTES DE TEST:")
            print("   Administrateur: username=admin, password=admin123")
            print("   Manager: username=manager, password=manager123")
            print("   Vendeur: username=vendeur, password=vendeur123")
            print("   Vendeur: username=kone, password=kone123")
            
            print("\n📍 PRODUITS EN STOCK FAIBLE:")
            produits_faible = [p for p in produits if p.stock_actuel <= p.stock_min]
            for pf in produits_faible:
                print(f"   ⚠️  {pf.nom}: {pf.stock_actuel} unités (min: {pf.stock_min})")
            
            if not produits_faible:
                print("   ✅ Aucun produit en stock faible")
            
            print("\n💰 VALEUR DU STOCK TOTAL:")
            valeur_stock = sum(p.stock_actuel * p.prix_achat for p in produits)
            print(f"   💵 {valeur_stock:,.0f} F CFA")
            
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création des données: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    success = create_sample_data()
    if success:
        print("\n✅ Le script de seed s'est terminé avec succès!")
        print("🚀 Vous pouvez maintenant démarrer l'application avec: python run.py")
    else:
        print("\n❌ Le script de seed a échoué!")
        sys.exit(1)