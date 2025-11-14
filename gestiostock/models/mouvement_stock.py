from datetime import datetime
from . import db

class MouvementStock(db.Model):
    __tablename__ = 'mouvements_stock'
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    type_mouvement = db.Column(db.String(20), nullable=False)  # entrée, sortie, ajustement, retour
    quantite = db.Column(db.Integer, nullable=False)
    quantite_avant = db.Column(db.Integer)
    quantite_apres = db.Column(db.Integer)
    motif = db.Column(db.String(200))
    cout_unitaire = db.Column(db.Float)
    reference_document = db.Column(db.String(100))
    date_mouvement = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'produit': self.produit.nom if self.produit else 'Produit inconnu',
            'type': self.type_mouvement,
            'quantite': self.quantite,
            'quantite_avant': self.quantite_avant,
            'quantite_apres': self.quantite_apres,
            'motif': self.motif,
            'date': self.date_mouvement.strftime('%Y-%m-%d %H:%M')
        }