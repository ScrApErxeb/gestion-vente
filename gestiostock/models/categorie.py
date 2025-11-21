from datetime import datetime
from . import db

class Categorie(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    produits = db.relationship('Produit', backref='categorie', lazy=True)
    sous_categories = db.relationship('Categorie', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'parent_id': self.parent_id,
            'actif': self.actif,
        }