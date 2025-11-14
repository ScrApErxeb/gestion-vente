from datetime import datetime
from . import db

class Fournisseur(db.Model):
    __tablename__ = 'fournisseurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    telephone2 = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(100))
    pays = db.Column(db.String(100), default='Burkina Faso')
    site_web = db.Column(db.String(200))
    num_contribuable = db.Column(db.String(50))
    conditions_paiement = db.Column(db.String(100))
    delai_livraison = db.Column(db.Integer)  # en jours
    devise_preferee = db.Column(db.String(10), default='XOF')
    notes = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    produits = db.relationship('Produit', backref='fournisseur', lazy=True)
    commandes = db.relationship('Commande', backref='fournisseur', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'contact': self.contact,
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse,
            'ville': self.ville,
            'conditions_paiement': self.conditions_paiement,
            'actif': self.actif
        }