from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    telephone = db.Column(db.String(20))
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    dernier_login = db.Column(db.DateTime)
    preferences = db.Column(db.Text)  # JSON pour préférences (devise, langue, etc.)
    
    # Relations seront définies après l'import des autres modèles
    # ventes = db.relationship('Vente', backref='utilisateur', lazy=True, foreign_keys='Vente.user_id')
    # commandes = db.relationship('Commande', backref='utilisateur', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nom': self.nom,
            'prenom': self.prenom,
            'role': self.role,
            'telephone': self.telephone,
            'actif': self.actif
        }