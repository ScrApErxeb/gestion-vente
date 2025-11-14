from datetime import datetime
from . import db

class Vente(db.Model):
    __tablename__ = 'ventes'
    id = db.Column(db.Integer, primary_key=True)
    numero_facture = db.Column(db.String(50), unique=True, nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    remise = db.Column(db.Float, default=0.0)
    tva = db.Column(db.Float, default=0.0)
    montant_total = db.Column(db.Float, nullable=False)
    devise = db.Column(db.String(10), default='XOF')
    mode_paiement = db.Column(db.String(20), default='espèces')
    date_vente = db.Column(db.DateTime, default=datetime.utcnow)
    date_echeance = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default='confirmée')
    statut_paiement = db.Column(db.String(20), default='payé')
    notes = db.Column(db.Text)
    
    # Pas de relations définies ici - elles seront gérées dans __init__.py
    
    def to_dict(self):
        """Version sécurisée sans dépendance aux relations"""
        from .produit import Produit
        from .client import Client
        
        # Charger manuellement les relations si nécessaire
        produit = Produit.query.get(self.produit_id) if self.produit_id else None
        client = Client.query.get(self.client_id) if self.client_id else None
        
        return {
            'id': self.id,
            'numero_facture': self.numero_facture,
            'produit': produit.nom if produit else 'Produit inconnu',
            'produit_id': self.produit_id,
            'client': f"{client.nom} {client.prenom}" if client else "Client anonyme",
            'client_id': self.client_id,
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'remise': self.remise,
            'montant_total': self.montant_total,
            'devise': self.devise,
            'mode_paiement': self.mode_paiement,
            'date_vente': self.date_vente.strftime('%Y-%m-%d %H:%M') if self.date_vente else None,
            'statut': self.statut,
            'statut_paiement': self.statut_paiement
        }

class VenteItem(db.Model):
    __tablename__ = 'vente_items'
    id = db.Column(db.Integer, primary_key=True)
    vente_id = db.Column(db.Integer, db.ForeignKey('ventes.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    montant_total = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        from .produit import Produit
        produit = Produit.query.get(self.produit_id) if self.produit_id else None
        
        return {
            'id': self.id,
            'vente_id': self.vente_id,
            'produit': produit.nom if produit else 'Produit inconnu',
            'produit_id': self.produit_id,
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'montant_total': self.montant_total
        }