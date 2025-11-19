from . import db

def configure_relationships():
    """Configure toutes les relations SQLAlchemy avec des noms uniques"""
    
    # Importer les modèles localement pour éviter les imports circulaires
    from .user import User
    from .vente import Vente, VenteItem
    from .produit import Produit
    from .client import Client
    from .commande import Commande, CommandeItem
    from .categorie import Categorie
    from .fournisseur import Fournisseur
    from .mouvement_stock import MouvementStock
    from .paiement import Paiement
    from .notification import Notification
    from .parametre_systeme import ParametreSysteme
    
    # === RELATIONS UTILISATEUR ===
    User.ventes_crees = db.relationship('Vente', backref='createur_vente', lazy=True, foreign_keys='Vente.user_id')
    User.commandes_crees = db.relationship('Commande', backref='createur_commande', lazy=True, foreign_keys='Commande.user_id')
    User.notifications_recues = db.relationship('Notification', backref='destinataire_notification', lazy=True)
    
    # === RELATIONS CATÉGORIE ===
    Categorie.produits_associes = db.relationship('Produit', backref='categorie_associee', lazy=True)
    Categorie.sous_categories_associees = db.relationship('Categorie', backref=db.backref('categorie_parente', remote_side='Categorie.id'))
    
    # === RELATIONS PRODUIT ===
    Produit.ventes_associees = db.relationship('Vente', backref='produit_vendu', lazy=True)
    Produit.mouvements_stock = db.relationship('MouvementStock', backref='produit_mouvement', lazy=True)
    Produit.items_commandes = db.relationship('CommandeItem', backref='produit_commande', lazy=True)
    Produit.fournisseur_associe = db.relationship('Fournisseur', backref='produits_fournis', lazy=True)
    
    # === RELATIONS CLIENT ===
    Client.ventes_effectuees = db.relationship('Vente', backref='client_acheteur', lazy=True)
    
    # === RELATIONS FOURNISSEUR ===
    Fournisseur.commandes_passees = db.relationship('Commande', backref='fournisseur_commande', lazy=True)
    
    # === RELATIONS VENTE ===
    Vente.items_vente = db.relationship('VenteItem', backref='vente_associee', lazy=True, cascade='all, delete-orphan')
    Vente.paiements_effectues = db.relationship('Paiement', backref='vente_payee', lazy=True, cascade='all, delete-orphan')
    
    # === RELATIONS VENTE ITEM ===
    # Les relations sont déjà définies par les backrefs
    
    # === RELATIONS COMMANDE ===
    Commande.items_commande = db.relationship('CommandeItem', backref='commande_associee', lazy=True, cascade='all, delete-orphan')
    Commande.paiements_fournisseur = db.relationship('Paiement', backref='commande_payee', lazy=True, cascade='all, delete-orphan')
    
    # === RELATIONS COMMANDE ITEM ===
    # Les relations sont déjà définies par les backrefs
    
    # === RELATIONS MOUVEMENT STOCK ===
    # Les relations sont déjà définies par les backrefs
    
    # === RELATIONS PAIEMENT ===
    # Les relations sont déjà définies par les backrefs
    
    # === RELATIONS NOTIFICATION ===
    # Les relations sont déjà définies par les backrefs
    
    # === RELATIONS PARAMÈTRE SYSTÈME ===
    # Pas de relations
    
    print("✅ Relations SQLAlchemy configurées avec succès (noms uniques)")