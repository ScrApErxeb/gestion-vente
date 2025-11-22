from datetime import datetime
from . import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    entreprise = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True)
    telephone = db.Column(db.String(20))
    telephone2 = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(100))
    pays = db.Column(db.String(100), default='Burkina Faso')
    code_postal = db.Column(db.String(20))
    type_client = db.Column(db.String(20), default='particulier')  # particulier, professionnel
    num_contribuable = db.Column(db.String(50))
    remise_defaut = db.Column(db.Float, default=0.0)
    plafond_credit = db.Column(db.Float, default=0.0)
    devise_preferee = db.Column(db.String(10), default='XOF')
    notes = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    
    @property
    def total_achats(self):
        try:
            return sum(v.montant_total for v in self.ventes if v.statut == 'confirmée')
        except (TypeError, AttributeError):
            return 0.0
    
    @property
    def nombre_achats(self):
        return len([v for v in self.ventes if v.statut == 'confirmée'])
    

    __table_args__ = (
        db.Index('idx_client_nom', 'nom'),
        db.Index('idx_client_email', 'email'),
        db.Index('idx_client_entreprise', 'entreprise'),
        db.Index('idx_client_actif', 'actif'),
    )
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'entreprise': self.entreprise,
            'email': self.email,
            'telephone': self.telephone,
            'adresse': self.adresse,
            'ville': self.ville,
            'type_client': self.type_client,
            'remise_defaut': self.remise_defaut,
            'total_achats': self.total_achats,
            'nombre_achats': self.nombre_achats,
            'actif': self.actif
        }