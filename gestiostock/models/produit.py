from datetime import datetime
from . import db

class Produit(db.Model):
    __tablename__ = 'produits'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    code_barre = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    prix_achat = db.Column(db.Float, nullable=False)
    prix_vente = db.Column(db.Float, nullable=False)
    tva = db.Column(db.Float, default=0.0)
    stock_actuel = db.Column(db.Integer, default=0)
    stock_min = db.Column(db.Integer, default=0)
    stock_max = db.Column(db.Integer, default=1000)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseurs.id'))
    image_url = db.Column(db.String(255))
    poids = db.Column(db.Float)
    unite_mesure = db.Column(db.String(20), default='unité')
    emplacement = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations seront définies après
    # ventes = db.relationship('Vente', backref='produit', lazy=True)
    # mouvements = db.relationship('MouvementStock', backref='produit', lazy=True)
    # commande_items = db.relationship('CommandeItem', backref='produit', lazy=True)
    
    @property
    def stock_faible(self):
        return self.stock_actuel <= self.stock_min
    
    @property
    def marge_benefice(self):
        return ((self.prix_vente - self.prix_achat) / self.prix_achat * 100) if self.prix_achat > 0 else 0
    
    @property
    def valeur_stock(self):
        return self.stock_actuel * self.prix_achat
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'reference': self.reference,
            # ... autres champs ...
            'categorie': self.categorie_rel.nom if self.categorie_rel else None,
            'fournisseur': self.fournisseur_rel.nom if self.fournisseur_rel else None,
            'stock_faible': self.stock_faible,
            'marge_benefice': self.marge_benefice,
            'valeur_stock': self.valeur_stock,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'actif': self.actif,
            
            }