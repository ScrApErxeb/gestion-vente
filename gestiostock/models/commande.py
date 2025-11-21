from datetime import datetime
from . import db

class Commande(db.Model):
    __tablename__ = 'commandes'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_commande = db.Column(db.String(50), unique=True, nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseurs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)
    date_livraison_prevue = db.Column(db.DateTime)
    date_livraison_reelle = db.Column(db.DateTime)
    montant_total = db.Column(db.Float, nullable=False)
    devise = db.Column(db.String(10), default='XOF')
    statut = db.Column(db.String(20), default='en_attente')
    statut_paiement = db.Column(db.String(20), default='impayé')
    mode_paiement = db.Column(db.String(20))
    notes = db.Column(db.Text)
    
    # ⚠️ SUPPRIMEZ ces lignes - les relations sont dans configure_relationships()
    # fournisseur = db.relationship('Fournisseur', backref='commandes', lazy=True)
    # items = db.relationship('CommandeItem', backref='commande', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_commande_numero', 'numero_commande'),
        db.Index('idx_commande_fournisseur', 'fournisseur_id'),
        db.Index('idx_commande_date', 'date_commande'),
        db.Index('idx_commande_statut', 'statut'),
    )

    def to_dict(self):
        """Convertit la commande en dictionnaire pour l'API"""
        try:
            data = {
                'id': self.id,
                'numero_commande': self.numero_commande,
                'date_commande': self.date_commande.isoformat() if self.date_commande else None,
                'date_livraison_prevue': self.date_livraison_prevue.isoformat() if self.date_livraison_prevue else None,
                'date_livraison_reelle': self.date_livraison_reelle.isoformat() if self.date_livraison_reelle else None,
                'montant_total': float(self.montant_total),
                'devise': self.devise,
                'statut': self.statut,
                'statut_paiement': self.statut_paiement,
                'mode_paiement': self.mode_paiement,
                'notes': self.notes,
                'fournisseur_id': self.fournisseur_id,
                'user_id': self.user_id
            }
            
            # ⭐ UTILISEZ les noms de relations de configure_relationships()
            if hasattr(self, 'fournisseur_commande') and self.fournisseur_commande:
                data['fournisseur'] = self.fournisseur_commande.nom
            else:
                data['fournisseur'] = f"Fournisseur ID:{self.fournisseur_id}"
                
            # Compter les items
            if hasattr(self, 'items_commande'):
                data['nb_items'] = len(self.items_commande)
            else:
                data['nb_items'] = 0
                
            return data
            
        except Exception as e:
            print(f"❌ Erreur dans commande.to_dict(): {e}")
            return {
                'id': self.id,
                'numero_commande': self.numero_commande,
                'fournisseur': 'Erreur chargement',
                'montant_total': float(self.montant_total) if self.montant_total else 0,
                'statut': self.statut
            }


class CommandeItem(db.Model):
    __tablename__ = 'commande_items'
    
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    quantite_commandee = db.Column(db.Integer, nullable=False)
    quantite_recue = db.Column(db.Integer, default=0)
    prix_unitaire = db.Column(db.Float, nullable=False)
    montant_total = db.Column(db.Float, nullable=False)
    
    # ⚠️ SUPPRIMEZ cette ligne - la relation est dans configure_relationships()
    # produit = db.relationship('Produit', backref='commande_items', lazy=True)
    
    __table_args__ = (
        db.Index('idx_commande_item_commande', 'commande_id'),
        db.Index('idx_commande_item_produit', 'produit_id'),
        db.Index('idx_commande_item_quantite', 'quantite_commandee'),
    )

    def to_dict(self):
        """Convertit l'item de commande en dictionnaire pour l'API"""
        try:
            data = {
                'id': self.id,
                'commande_id': self.commande_id,
                'produit_id': self.produit_id,
                'quantite_commandee': self.quantite_commandee,
                'quantite_recue': self.quantite_recue,
                'prix_unitaire': float(self.prix_unitaire),
                'montant_total': float(self.montant_total)
            }
            
            # ⭐ UTILISEZ les noms de relations de configure_relationships()
            if hasattr(self, 'produit_commande') and self.produit_commande:
                data['produit'] = self.produit_commande.nom
            else:
                data['produit'] = f"Produit ID:{self.produit_id}"
                
            return data
            
        except Exception as e:
            print(f"❌ Erreur dans commande_item.to_dict(): {e}")
            return {
                'id': self.id,
                'produit': 'Erreur chargement',
                'quantite_commandee': self.quantite_commandee,
                'prix_unitaire': float(self.prix_unitaire)
            }