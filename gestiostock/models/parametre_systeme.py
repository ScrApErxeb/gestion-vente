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
            try:
                return float(param.valeur)
            except:
                return default

        return param.valeur
    
    @classmethod
    def set_value(cls, cle, valeur, type_valeur='string'):
        param = cls.query.filter_by(cle=cle).first()
        
        if type_valeur == 'json':
            valeur_formatee = json.dumps(valeur)
        else:
            valeur_formatee = str(valeur)

        if param:
            param.valeur = valeur_formatee
            param.type_valeur = type_valeur
        else:
            param = cls(cle=cle, valeur=valeur_formatee, type_valeur=type_valeur)
            db.session.add(param)
        
        db.session.commit()


# 🟦 IMPORTANT : initialiser la caisse si elle n'existe pas
def initialiser_solde_caisse():
    if ParametreSysteme.get_value("solde_caisse") is None:
        ParametreSysteme.set_value("solde_caisse", 0, type_valeur="number")
