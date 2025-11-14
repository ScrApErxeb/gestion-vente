from datetime import datetime
from . import db

class Paiement(db.Model):
    __tablename__ = 'paiements'
    id = db.Column(db.Integer, primary_key=True)
    vente_id = db.Column(db.Integer, db.ForeignKey('ventes.id'))
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'))
    montant = db.Column(db.Float, nullable=False)
    mode_paiement = db.Column(db.String(20), nullable=False)
    reference = db.Column(db.String(100))
    date_paiement = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'montant': self.montant,
            'mode_paiement': self.mode_paiement,
            'reference': self.reference,
            'date_paiement': self.date_paiement.strftime('%Y-%m-%d %H:%M')
        }