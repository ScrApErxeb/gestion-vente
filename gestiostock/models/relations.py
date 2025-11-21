def configure_relationships():
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
    from . import db

    # === UTILISATEUR ===
    User.ventes_crees = db.relationship('Vente', back_populates='createur', lazy=True, foreign_keys='Vente.user_id')
    Vente.createur = db.relationship('User', back_populates='ventes_crees', foreign_keys='Vente.user_id')

    User.commandes_crees = db.relationship('Commande', back_populates='createur', lazy=True, foreign_keys='Commande.user_id')
    Commande.createur = db.relationship('User', back_populates='commandes_crees', foreign_keys='Commande.user_id')

    User.notifications_recues = db.relationship('Notification', back_populates='destinataire', lazy=True)
    Notification.destinataire = db.relationship('User', back_populates='notifications_recues')

    # === CATÉGORIES ===
    Categorie.produits = db.relationship('Produit', back_populates='categorie', lazy=True)
    Produit.categorie = db.relationship('Categorie', back_populates='produits', lazy=True)

    Categorie.parent = db.relationship('Categorie', remote_side='Categorie.id', back_populates='sous_categories')
    Categorie.sous_categories = db.relationship('Categorie', back_populates='parent', lazy=True)

    # === PRODUIT ===
    Produit.ventes_items = db.relationship('VenteItem', back_populates='produit', lazy=True, overlaps='produit')
    VenteItem.produit = db.relationship('Produit', back_populates='ventes_items', lazy=True)

    Produit.commandes_items = db.relationship('CommandeItem', back_populates='produit', lazy=True, overlaps='produit_lie')
    CommandeItem.produit = db.relationship('Produit', back_populates='commandes_items', lazy=True)

    Produit.fournisseur = db.relationship('Fournisseur', back_populates='produits', lazy=True, foreign_keys='Produit.fournisseur_id')
    Fournisseur.produits = db.relationship('Produit', back_populates='fournisseur', lazy=True)

    Produit.mouvements_stock = db.relationship('MouvementStock', back_populates='produit', lazy=True)
    MouvementStock.produit = db.relationship('Produit', back_populates='mouvements_stock')

    # === CLIENT ===
    Client.ventes = db.relationship('Vente', back_populates='client', lazy=True)
    Vente.client = db.relationship('Client', back_populates='ventes', lazy=True)

    # === VENTE ===
    Vente.items = db.relationship('VenteItem', back_populates='vente', lazy=True, cascade='all, delete-orphan')
    VenteItem.vente = db.relationship('Vente', back_populates='items')

    Vente.paiements = db.relationship('Paiement', back_populates='vente', lazy=True, cascade='all, delete-orphan')
    Paiement.vente = db.relationship('Vente', back_populates='paiements')

    # === COMMANDE ===
    Commande.items = db.relationship('CommandeItem', back_populates='commande', lazy=True, cascade='all, delete-orphan')
    CommandeItem.commande = db.relationship('Commande', back_populates='items')

    Commande.paiements = db.relationship('Paiement', back_populates='commande', lazy=True, cascade='all, delete-orphan')
    Paiement.commande = db.relationship('Commande', back_populates='paiements')

    # === NOTIFICATION ===
    # Déjà configuré dans User

    print("✅ Relations SQLAlchemy configurées proprement avec back_populates")
