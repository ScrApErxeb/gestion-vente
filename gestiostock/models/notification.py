from datetime import datetime
from . import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(50))  # stock_faible, vente, commande, etc.
    titre = db.Column(db.String(200))
    message = db.Column(db.Text)
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'titre': self.titre,
            'message': self.message,
            'lue': self.lue,
            'date': self.date_creation.strftime('%Y-%m-%d %H:%M')
        }