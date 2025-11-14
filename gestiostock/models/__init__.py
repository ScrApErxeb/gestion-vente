from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import des modèles après la création de db
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

# Configuration des relations circulaires après l'import de tous les modèles
def configure_relationships():
    from .user import User
    from .vente import Vente
    from .commande import Commande
    from .produit import Produit
    
    # Relations pour User
    if not hasattr(User, 'ventes'):
        User.ventes = db.relationship('Vente', backref='utilisateur_relation', lazy=True, foreign_keys='Vente.user_id')
    
    if not hasattr(User, 'commandes'):
        User.commandes = db.relationship('Commande', backref='utilisateur_relation', lazy=True)
    
    # Relations pour Produit
    if not hasattr(Produit, 'ventes'):
        Produit.ventes_rel = db.relationship('Vente', backref='produit_relation', lazy=True)
    
    if not hasattr(Produit, 'mouvements'):
        Produit.mouvements = db.relationship('MouvementStock', backref='produit', lazy=True)
    
    if not hasattr(Produit, 'commande_items'):
        Produit.commande_items = db.relationship('CommandeItem', backref='produit', lazy=True)

# Appeler la configuration des relations
configure_relationships()

__all__ = [
    'db',
    'User', 'Categorie', 'Produit', 'Client', 'Vente', 'VenteItem',
    'Paiement', 'MouvementStock', 'Fournisseur', 'Commande', 'CommandeItem',
    'Notification', 'ParametreSysteme'
]