import json
from . import db

class ParametreSysteme(db.Model):
    __tablename__ = 'parametres_systeme'
    id = db.Column(db.Integer, primary_key=True)
    cle = db.Column(db.String(100), unique=True, nullable=False)
    valeur = db.Column(db.Text)
    description = db.Column(db.Text)
    type_valeur = db.Column(db.String(20), default='string')  # string, number, boolean, json
    
    @classmethod
    def get_value(cls, cle, default=None):
        param = cls.query.filter_by(cle=cle).first()
        if not param:
            return default
        if param.type_valeur == 'json':
            return json.loads(param.valeur)
        elif param.type_valeur == 'boolean':
            return param.valeur.lower() == 'true'
        elif param.type_valeur == 'number':
            return float(param.valeur)
        return param.valeur
    
    @classmethod
    def set_value(cls, cle, valeur, type_valeur='string'):
        param = cls.query.filter_by(cle=cle).first()
        if param:
            param.valeur = str(valeur) if type_valeur != 'json' else json.dumps(valeur)
        else:
            param = cls(cle=cle, valeur=str(valeur) if type_valeur != 'json' else json.dumps(valeur), type_valeur=type_valeur)
            db.session.add(param)
        db.session.commit()