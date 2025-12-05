from . import db
from datetime import datetime

class Depense(db.Model):
    __tablename__ = 'depenses'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(120), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Depense {self.libelle} - {self.montant}>"
