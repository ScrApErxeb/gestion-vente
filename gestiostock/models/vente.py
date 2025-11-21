from datetime import datetime
from . import db

class Vente(db.Model):
    __tablename__ = 'ventes'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_facture = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
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

    def to_dict(self):
        """Retourne un dict complet de la vente avec les items"""
        try:
            return {
                'id': self.id,
                'numero_facture': self.numero_facture,
                'date_vente': self.date_vente.isoformat() if self.date_vente else None,
                'mode_paiement': self.mode_paiement,
                'devise': self.devise,
                'statut': self.statut,
                'statut_paiement': self.statut_paiement,
                'notes': self.notes,
                'client_id': self.client_id,
                'montant_total': float(self.montant_total) if self.montant_total else 0,
                'client': f"{self.client.nom} {self.client.prenom}".strip() if self.client else "Client anonyme",
                'items': [item.to_dict() for item in self.items]  # Utilise VenteItem.to_dict()
            }
        except Exception as e:
            print(f"❌ Erreur Vente.to_dict() pour {self.id}: {e}")
            return {
                'id': self.id,
                'numero_facture': self.numero_facture,
                'client': 'Erreur chargement',
                'montant_total': float(self.montant_total) if self.montant_total else 0
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

    def to_dict(self):
        """Retourne un dict détaillé de l'article de vente"""
        try:
            return {
                'id': self.id,
                'vente_id': self.vente_id,
                'produit_id': self.produit.id if self.produit else None,
                'produit_nom': self.produit.nom if self.produit else "Produit inconnu",
                'quantite': self.quantite,
                'prix_unitaire': float(self.prix_unitaire),
                'remise': float(self.remise or 0),
                'montant_total': float(self.prix_unitaire * self.quantite) - float(self.remise or 0)
            }
        except Exception as e:
            print(f"❌ Erreur VenteItem.to_dict() pour {self.id}: {e}")
            return {
                'id': self.id,
                'vente_id': self.vente_id,
                'produit_id': self.produit_id,
                'produit_nom': 'Erreur chargement',
                'quantite': self.quantite,
                'prix_unitaire': float(self.prix_unitaire),
                'remise': float(self.remise or 0),
                'montant_total': float(self.prix_unitaire * self.quantite) - float(self.remise or 0)
            }
