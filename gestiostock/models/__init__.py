from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import des modèles
from .user import User
from .categorie import Categorie
from .produit import Produit
from .client import Client
from .vente import Vente, VenteItem
from .paiement import Paiement
from .mouvement_stock import MouvementStock
from .fournisseur import Fournisseur
from .commande import Commande, CommandeItem
from .notification import Notification
from .parametre_systeme import ParametreSysteme

# Configuration des relations APRÈS tous les imports
def configure_relationships():
    from .vente import Vente, VenteItem
    from .produit import Produit
    from .client import Client
    from .user import User
    from .commande import Commande, CommandeItem
    
    # === RELATIONS POUR VENTE ===
    # Relation Vente -> Client (backref différent pour éviter les conflits)
    if not hasattr(Vente, 'client_rel'):
        Vente.client_rel = db.relationship('Client', backref='ventes_client', lazy=True, foreign_keys='Vente.client_id')
    
    # Relation Vente -> User (backref différent)
    if not hasattr(Vente, 'user_rel'):
        Vente.user_rel = db.relationship('User', backref='ventes_user', lazy=True, foreign_keys='Vente.user_id')
    
    # Relation Vente -> VenteItem
    if not hasattr(Vente, 'items_rel'):
        Vente.items_rel = db.relationship('VenteItem', backref='vente', lazy=True, cascade='all, delete-orphan')
    
    # === RELATIONS POUR VENTEITEM ===
    # Relation VenteItem -> Produit
    if not hasattr(VenteItem, 'produit_rel'):
        VenteItem.produit_rel = db.relationship('Produit', backref='vente_items', lazy=True)
    
    # === RELATIONS POUR PRODUIT ===
    # Relation Produit -> Catégorie
    if not hasattr(Produit, 'categorie_rel'):
        Produit.categorie_rel = db.relationship('Categorie', backref='produits_cat', lazy=True)
    
    # Relation Produit -> Fournisseur
    if not hasattr(Produit, 'fournisseur_rel'):
        Produit.fournisseur_rel = db.relationship('Fournisseur', backref='produits_fourn', lazy=True)
    
    # Relation Produit -> MouvementStock
    if not hasattr(Produit, 'mouvements_rel'):
        Produit.mouvements_rel = db.relationship('MouvementStock', backref='produit_mouv', lazy=True)
    
    # === RELATIONS POUR CLIENT ===
    # Relation Client -> Vente (utilise le backref de Vente.client_rel)
    # Pas besoin de définir ici, c'est géré par le backref
    
    # === RELATIONS POUR COMMANDE ===
    # Relation Commande -> Fournisseur
    if not hasattr(Commande, 'fournisseur_rel'):
        Commande.fournisseur_rel = db.relationship('Fournisseur', backref='commandes_fourn', lazy=True)
    
    # Relation Commande -> User
    if not hasattr(Commande, 'user_rel'):
        Commande.user_rel = db.relationship('User', backref='commandes_user', lazy=True)
    
    # Relation Commande -> CommandeItem
    if not hasattr(Commande, 'items_rel'):
        Commande.items_rel = db.relationship('CommandeItem', backref='commande', lazy=True, cascade='all, delete-orphan')
    
    # === RELATIONS POUR COMMANDEITEM ===
    # Relation CommandeItem -> Produit
    if not hasattr(CommandeItem, 'produit_rel'):
        CommandeItem.produit_rel = db.relationship('Produit', backref='commande_items', lazy=True)
    
    # === RELATIONS POUR USER ===
    # Relations déjà gérées par les backrefs
    
    # === RELATIONS POUR MOUVEMENTSTOCK ===
    # Relation MouvementStock -> Produit (déjà gérée)

# Appeler la configuration
configure_relationships()

__all__ = [
    'db',
    'User', 'Categorie', 'Produit', 'Client', 'Vente', 'VenteItem',
    'Paiement', 'MouvementStock', 'Fournisseur', 'Commande', 'CommandeItem',
    'Notification', 'ParametreSysteme'
]