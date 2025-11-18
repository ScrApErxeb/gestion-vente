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
    __table_args__ = (
        db.Index('idx_vente_numero', 'numero_facture'),
        db.Index('idx_vente_client', 'client_id'),
        db.Index('idx_vente_date', 'date_vente'),
        db.Index('idx_vente_statut', 'statut'),
        db.Index('idx_vente_paiement', 'statut_paiement'),
    )


    def to_dict(self):
        return {
            'id': self.id,
            'numero_facture': self.numero_facture,
            'client': self.client_rel.to_dict() if self.client_rel else None,
            'utilisateur': self.user_rel.to_dict() if self.user_rel else None,
            'date_vente': self.date_vente.isoformat() if self.date_vente else None,
            'statut': self.statut,
            'statut_paiement': self.statut_paiement,
            'montant_total': self.montant_total,
            'nb_items': len(self.items_rel),
            'items': [item.to_dict() for item in self.items_rel]
        }    
    

    
class VenteItem(db.Model):
    __tablename__ = 'vente_items'
    id = db.Column(db.Integer, primary_key=True)
    vente_id = db.Column(db.Integer, db.ForeignKey('ventes.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    remise = db.Column(db.Float, default=0.0)
    tva = db.Column(db.Float, default=0.0)
    montant_total = db.Column(db.Float, nullable=False)
    
    # SUPPRIMER cette ligne si elle existe :
    # __table_args__ = (db.Index('idx_vente_item_reference', 'reference'),)
    
    # À la place, ajouter des index sur les colonnes existantes :
    __table_args__ = (
        db.Index('idx_vente_item_vente', 'vente_id'),
        db.Index('idx_vente_item_produit', 'produit_id'),
        db.Index('idx_vente_item_quantite', 'quantite'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'vente_id': self.vente_id,
            'produit_id': self.produit_id,
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'remise': self.remise,
            'tva': self.tva,
            'montant_total': self.montant_total
        }