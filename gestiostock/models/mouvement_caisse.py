from datetime import datetime
from . import db


class MouvementCaisse(db.Model):
    __tablename__ = 'mouvement_caisse'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'encaisse' ou 'decaisse'
    montant = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    paiement_id = db.Column(db.Integer, db.ForeignKey('paiements.id'))
    vente_id = db.Column(db.Integer, db.ForeignKey('ventes.id'))
    utilisateur = db.Column(db.String(100))
    solde_avant = db.Column(db.Float)
    solde_apres = db.Column(db.Float)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'montant': self.montant,
            'reference': self.reference,
            'date': self.date.strftime('%Y-%m-%d %H:%M') if self.date else None,
            'paiement_id': self.paiement_id,
            'vente_id': self.vente_id,
            'utilisateur': self.utilisateur,
            'solde_avant': self.solde_avant,
            'solde_apres': self.solde_apres,
            'notes': self.notes,
        }
