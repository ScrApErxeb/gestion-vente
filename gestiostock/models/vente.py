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
    
    # ⚠️ SUPPRIMEZ ces lignes - les relations sont dans configure_relationships()
    # produit = db.relationship('Produit', backref='ventes', lazy='joined')
    # client = db.relationship('Client', backref='ventes', lazy='joined')
    # user = db.relationship('User', backref='ventes', lazy='joined')
    
    __table_args__ = (
        db.Index('idx_vente_numero', 'numero_facture'),
        db.Index('idx_vente_client', 'client_id'),
        db.Index('idx_vente_date', 'date_vente'),
        db.Index('idx_vente_statut', 'statut'),
        db.Index('idx_vente_paiement', 'statut_paiement'),
    )

    def to_dict(self):
        """Convertit la vente en dictionnaire pour l'API"""
        try:
            data = {
                'id': self.id,
                'numero_facture': self.numero_facture,
                'date_vente': self.date_vente.isoformat() if self.date_vente else None,
                'produit_id': self.produit_id,
                'quantite': self.quantite,
                'prix_unitaire': float(self.prix_unitaire),
                'remise': float(self.remise),
                'montant_total': float(self.montant_total),
                'mode_paiement': self.mode_paiement,
                'devise': self.devise,
                'statut': self.statut,
                'statut_paiement': self.statut_paiement,
                'notes': self.notes,
                'client_id': self.client_id
            }
            
            # ⭐ UTILISEZ les noms de relations de configure_relationships()
            if hasattr(self, 'produit_vendu') and self.produit_vendu:
                data['produit'] = self.produit_vendu.nom
            else:
                data['produit'] = f"Produit ID:{self.produit_id}"
                
            if hasattr(self, 'client_acheteur') and self.client_acheteur:
                nom_complet = f"{self.client_acheteur.nom or ''} {self.client_acheteur.prenom or ''}".strip()
                data['client'] = nom_complet or "Client anonyme"
            else:
                data['client'] = "Client anonyme"
                
            return data
            
        except Exception as e:
            print(f"❌ Erreur dans vente.to_dict(): {e}")
            return {
                'id': self.id,
                'numero_facture': self.numero_facture,
                'produit': 'Erreur chargement',
                'client': 'Erreur chargement',
                'quantite': self.quantite,
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
    
    # ⚠️ SUPPRIMEZ ces lignes aussi
    # vente = db.relationship('Vente', backref='items_vente', lazy='joined')
    # produit = db.relationship('Produit', backref='vente_items', lazy='joined')
    
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