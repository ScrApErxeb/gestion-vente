from datetime import datetime
from . import db

class Commande(db.Model):
    __tablename__ = 'commandes'
    id = db.Column(db.Integer, primary_key=True)
    numero_commande = db.Column(db.String(50), unique=True, nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseurs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)
    date_livraison_prevue = db.Column(db.DateTime)
    date_livraison_reelle = db.Column(db.DateTime)
    montant_total = db.Column(db.Float, nullable=False)
    devise = db.Column(db.String(10), default='XOF')
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, confirmée, reçue, annulée
    statut_paiement = db.Column(db.String(20), default='impayé')
    mode_paiement = db.Column(db.String(20))
    notes = db.Column(db.Text)
    
    # Relations
    items = db.relationship('CommandeItem', backref='commande', lazy=True, cascade='all, delete-orphan')
    paiements = db.relationship('Paiement', backref='commande', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_commande': self.numero_commande,
            'fournisseur': self.fournisseur.nom if self.fournisseur else 'Fournisseur inconnu',
            'date_commande': self.date_commande.strftime('%Y-%m-%d'),
            'date_livraison_prevue': self.date_livraison_prevue.strftime('%Y-%m-%d') if self.date_livraison_prevue else None,
            'montant_total': self.montant_total,
            'devise': self.devise,
            'statut': self.statut,
            'statut_paiement': self.statut_paiement,
            'nb_items': len(self.items)
        }

class CommandeItem(db.Model):
    __tablename__ = 'commande_items'
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    quantite_commandee = db.Column(db.Integer, nullable=False)
    quantite_recue = db.Column(db.Integer, default=0)
    prix_unitaire = db.Column(db.Float, nullable=False)
    montant_total = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'produit': self.produit.nom if self.produit else 'Produit inconnu',
            'quantite_commandee': self.quantite_commandee,
            'quantite_recue': self.quantite_recue,
            'prix_unitaire': self.prix_unitaire,
            'montant_total': self.montant_total
        }