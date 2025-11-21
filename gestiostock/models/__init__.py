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
# Configuration des relations
from .relations import configure_relationships

# Appeler la configuration
configure_relationships()

__all__ = [
    'db',
    'User', 'Categorie', 'Produit', 'Client', 'Vente', 'VenteItem',
    'Paiement', 'MouvementStock', 'Fournisseur', 'Commande', 'CommandeItem',
    'Notification', 'ParametreSysteme'
]