"""
GestioStock - Système de Gestion de Stock Complet
Version Pro avec toutes les fonctionnalités avancées
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract
import os
import io
import json
from decimal import Decimal

# Imports pour export PDF/Excel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

# Configuration de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre-cle-secrete-super-securisee-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestiostock_pro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration multi-devises
app.config['CURRENCIES'] = {
    'XOF': {'symbol': 'F CFA', 'rate': 1.0, 'name': 'Franc CFA'},
    'EUR': {'symbol': '€', 'rate': 656.0, 'name': 'Euro'},
    'USD': {'symbol': '$', 'rate': 610.0, 'name': 'Dollar US'},
    'GBP': {'symbol': '£', 'rate': 765.0, 'name': 'Livre Sterling'}
}
app.config['DEFAULT_CURRENCY'] = 'XOF'

# Configuration Email/SMS (à configurer selon votre fournisseur)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'votre-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'votre-mot-de-passe'
app.config['SMS_API_KEY'] = 'votre-cle-api-sms'
app.config['SMS_SENDER'] = 'GestioStock'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==================== MODÈLES ====================

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
    
    ventes = db.relationship('Vente', backref='utilisateur', lazy=True, foreign_keys='Vente.user_id')
    commandes = db.relationship('Commande', backref='utilisateur', lazy=True)
    
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Categorie(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    actif = db.Column(db.Boolean, default=True)
    
    produits = db.relationship('Produit', backref='categorie', lazy=True)
    sous_categories = db.relationship('Categorie', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'nb_produits': len(self.produits),
            'actif': self.actif
        }

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
    
    ventes = db.relationship('Vente', backref='produit', lazy=True)
    mouvements = db.relationship('MouvementStock', backref='produit', lazy=True)
    commande_items = db.relationship('CommandeItem', backref='produit', lazy=True)
    
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
            'code_barre': self.code_barre,
            'description': self.description,
            'prix_achat': self.prix_achat,
            'prix_vente': self.prix_vente,
            'tva': self.tva,
            'stock_actuel': self.stock_actuel,
            'stock_min': self.stock_min,
            'stock_max': self.stock_max,
            'categorie': self.categorie.nom if self.categorie else None,
            'fournisseur': self.fournisseur.nom if self.fournisseur else None,
            'stock_faible': self.stock_faible,
            'marge_benefice': round(self.marge_benefice, 2),
            'valeur_stock': self.valeur_stock,
            'unite_mesure': self.unite_mesure,
            'actif': self.actif
        }

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
    
    ventes = db.relationship('Vente', backref='client', lazy=True)
    
    @property
    def total_achats(self):
        return sum(v.montant_total for v in self.ventes if v.statut == 'confirmée')
    
    @property
    def nombre_achats(self):
        return len([v for v in self.ventes if v.statut == 'confirmée'])
    
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

class Vente(db.Model):
    __tablename__ = 'ventes'
    id = db.Column(db.Integer, primary_key=True)
    numero_facture = db.Column(db.String(50), unique=True, nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    remise = db.Column(db.Float, default=0.0)
    tva = db.Column(db.Float, default=0.0)
    montant_total = db.Column(db.Float, nullable=False)
    devise = db.Column(db.String(10), default='XOF')
    mode_paiement = db.Column(db.String(20), default='espèces')  # espèces, carte, virement, mobile
    date_vente = db.Column(db.DateTime, default=datetime.utcnow)
    date_echeance = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default='confirmée')  # confirmée, annulée, en_attente
    statut_paiement = db.Column(db.String(20), default='payé')  # payé, impayé, partiel
    notes = db.Column(db.Text)
    
    paiements = db.relationship('Paiement', backref='vente', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_facture': self.numero_facture,
            'produit': self.produit.nom,
            'client': f"{self.client.nom} {self.client.prenom}" if self.client else "Client anonyme",
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'remise': self.remise,
            'montant_total': self.montant_total,
            'devise': self.devise,
            'mode_paiement': self.mode_paiement,
            'date_vente': self.date_vente.strftime('%Y-%m-%d %H:%M'),
            'statut': self.statut,
            'statut_paiement': self.statut_paiement
        }

class Paiement(db.Model):
    __tablename__ = 'paiements'
    id = db.Column(db.Integer, primary_key=True)
    vente_id = db.Column(db.Integer, db.ForeignKey('ventes.id'))
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'))
    montant = db.Column(db.Float, nullable=False)
    mode_paiement = db.Column(db.String(20), nullable=False)
    reference = db.Column(db.String(100))
    date_paiement = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'montant': self.montant,
            'mode_paiement': self.mode_paiement,
            'reference': self.reference,
            'date_paiement': self.date_paiement.strftime('%Y-%m-%d %H:%M')
        }

class MouvementStock(db.Model):
    __tablename__ = 'mouvements_stock'
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    type_mouvement = db.Column(db.String(20), nullable=False)  # entrée, sortie, ajustement, retour
    quantite = db.Column(db.Integer, nullable=False)
    quantite_avant = db.Column(db.Integer)
    quantite_apres = db.Column(db.Integer)
    motif = db.Column(db.String(200))
    cout_unitaire = db.Column(db.Float)
    reference_document = db.Column(db.String(100))
    date_mouvement = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'produit': self.produit.nom,
            'type': self.type_mouvement,
            'quantite': self.quantite,
            'quantite_avant': self.quantite_avant,
            'quantite_apres': self.quantite_apres,
            'motif': self.motif,
            'date': self.date_mouvement.strftime('%Y-%m-%d %H:%M')
        }

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
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, confirmée, reçue, annulée
    statut_paiement = db.Column(db.String(20), default='impayé')
    mode_paiement = db.Column(db.String(20))
    notes = db.Column(db.Text)
    
    items = db.relationship('CommandeItem', backref='commande', lazy=True, cascade='all, delete-orphan')
    paiements = db.relationship('Paiement', backref='commande', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_commande': self.numero_commande,
            'fournisseur': self.fournisseur.nom,
            'date_commande': self.date_commande.strftime('%Y-%m-%d'),
            'date_livraison_prevue': self.date_livraison_prevue.strftime('%Y-%m-%d') if self.date_livraison_prevue else None,
            'montant_total': self.montant_total,
            'devise': self.devise,
            'statut': self.statut,
            'statut_paiement': self.statut_paiement,
            'nb_items': len(self.items)
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'produit': self.produit.nom,
            'quantite_commandee': self.quantite_commandee,
            'quantite_recue': self.quantite_recue,
            'prix_unitaire': self.prix_unitaire,
            'montant_total': self.montant_total
        }

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

# ==================== UTILITAIRES ====================

def convertir_devise_util(montant, devise_source, devise_cible):
    """Convertit un montant d'une devise à une autre"""
    if devise_source == devise_cible:
        return montant
    
    currencies = app.config['CURRENCIES']
    if devise_source not in currencies or devise_cible not in currencies:
        return montant
    
    # Convertir en devise de base (XOF)
    montant_base = montant / currencies[devise_source]['rate']
    # Convertir en devise cible
    return montant_base * currencies[devise_cible]['rate']

def envoyer_notification(user_id, type_notif, titre, message):
    """Crée une notification pour un utilisateur"""
    notif = Notification(
        user_id=user_id,
        type=type_notif,
        titre=titre,
        message=message
    )
    db.session.add(notif)
    db.session.commit()
    return notif

def envoyer_email(destinataire, sujet, corps):
    """Envoie un email (à implémenter avec votre service SMTP)"""
    # Implémentation simplifiée - à adapter selon votre service
    print(f"Email envoyé à {destinataire}: {sujet}")
    return True

def envoyer_sms(telephone, message):
    """Envoie un SMS (à implémenter avec votre service SMS)"""
    # Implémentation simplifiée - à adapter selon votre service
    print(f"SMS envoyé à {telephone}: {message}")
    return True

def verifier_stock_faible():
    """Vérifie et envoie des alertes pour les produits en stock faible"""
    produits_faible = Produit.query.filter(
        Produit.stock_actuel <= Produit.stock_min,
        Produit.actif == True
    ).all()
    
    if produits_faible:
        # Notifier les admins
        admins = User.query.filter_by(role='admin', actif=True).all()
        for admin in admins:
            message = f"{len(produits_faible)} produit(s) en stock faible nécessitent une attention"
            envoyer_notification(admin.id, 'stock_faible', 'Alerte Stock', message)
    
    return produits_faible

# ==================== ROUTES AUTHENTIFICATION ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']) and user.actif:
            login_user(user)
            user.dernier_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'user': user.to_dict()})
        
        return jsonify({'success': False, 'message': 'Identifiants invalides'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        nom=data.get('nom'),
        prenom=data.get('prenom'),
        telephone=data.get('telephone'),
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/api/dashboard')
@login_required
def dashboard_data():
    """Données du tableau de bord avec analyse avancée"""
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    start_of_month = datetime(today.year, today.month, 1)
    start_of_year = datetime(today.year, 1, 1)
    
    # Devise de l'utilisateur
    user_prefs = json.loads(current_user.preferences) if current_user.preferences else {}
    devise = user_prefs.get('devise', app.config['DEFAULT_CURRENCY'])
    
    # Ventes
    ventes_jour = db.session.query(func.sum(Vente.montant_total)).filter(
        Vente.date_vente >= start_of_day,
        Vente.statut == 'confirmée'
    ).scalar() or 0
    
    ventes_mois = db.session.query(func.sum(Vente.montant_total)).filter(
        Vente.date_vente >= start_of_month,
        Vente.statut == 'confirmée'
    ).scalar() or 0
    
    ventes_annee = db.session.query(func.sum(Vente.montant_total)).filter(
        Vente.date_vente >= start_of_year,
        Vente.statut == 'confirmée'
    ).scalar() or 0
    
    # Commandes fournisseurs
    commandes_en_cours = Commande.query.filter(
        Commande.statut.in_(['en_attente', 'confirmée'])
    ).count()
    
    montant_commandes_en_cours = db.session.query(func.sum(Commande.montant_total)).filter(
        Commande.statut.in_(['en_attente', 'confirmée'])
    ).scalar() or 0
    
    # Statistiques produits
    nb_produits = Produit.query.filter_by(actif=True).count()
    produits_stock_faible = Produit.query.filter(
        Produit.stock_actuel <= Produit.stock_min,
        Produit.actif == True
    ).count()
    
    valeur_stock_total = db.session.query(
        func.sum(Produit.stock_actuel * Produit.prix_achat)
    ).filter_by(actif=True).scalar() or 0
    
    # Top produits vendus (mois en cours)
    top_produits = db.session.query(
        Produit.nom,
        func.sum(Vente.quantite).label('total_vendu'),
        func.sum(Vente.montant_total).label('ca')
    ).join(Vente).filter(
        Vente.date_vente >= start_of_month,
        Vente.statut == 'confirmée'
    ).group_by(Produit.id).order_by(func.sum(Vente.quantite).desc()).limit(5).all()
    
    # Ventes par mois (12 derniers mois)
    ventes_mensuelles = []
    for i in range(11, -1, -1):
        date = datetime.now() - timedelta(days=30*i)
        debut_mois = datetime(date.year, date.month, 1)
        if date.month == 12:
            fin_mois = datetime(date.year + 1, 1, 1)
        else:
            fin_mois = datetime(date.year, date.month + 1, 1)
        
        total = db.session.query(func.sum(Vente.montant_total)).filter(
            Vente.date_vente >= debut_mois,
            Vente.date_vente < fin_mois,
            Vente.statut == 'confirmée'
        ).scalar() or 0
        
        ventes_mensuelles.append({
            'mois': debut_mois.strftime('%b %Y'),
            'montant': total
        })
    
    # Statistiques clients
    nb_clients = Client.query.filter_by(actif=True).count()
    nouveaux_clients = Client.query.filter(Client.date_creation >= start_of_month).count()
    
    # Top clients
    top_clients = db.session.query(
        Client.nom,
        Client.prenom,
        func.sum(Vente.montant_total).label('total')
    ).join(Vente).filter(
        Vente.date_vente >= start_of_month,
        Vente.statut == 'confirmée'
    ).group_by(Client.id).order_by(func.sum(Vente.montant_total).desc()).limit(5).all()
    
    return jsonify({
        'ventes': {
            'jour': ventes_jour,
            'mois': ventes_mois,
            'annee': ventes_annee,
            'mensuelles': ventes_mensuelles
        },
        'commandes': {
            'en_cours': commandes_en_cours,
            'montant_en_cours': montant_commandes_en_cours
        },
        'produits': {
            'total': nb_produits,
            'stock_faible': produits_stock_faible,
            'valeur_stock': valeur_stock_total,
            'top_ventes': [{'nom': p[0], 'quantite': p[1], 'ca': p[2]} for p in top_produits]
        },
        'clients': {
            'total': nb_clients,
            'nouveaux': nouveaux_clients,
            'top_clients': [{'nom': f"{c[0]} {c[1]}", 'total': c[2]} for c in top_clients]
        },
        'devise': devise,
        'stats_globales': {
            'categories': Categorie.query.filter_by(actif=True).count(),
            'fournisseurs': Fournisseur.query.filter_by(actif=True).count(),
            'utilisateurs': User.query.filter_by(actif=True).count()
        }
    })

# ==================== ROUTES PRODUITS ====================

@app.route('/produits')
@login_required
def produits():
    return render_template('produits.html')

@app.route('/api/produits', methods=['GET'])
@login_required
def get_produits():
    search = request.args.get('search', '')
    categorie_id = request.args.get('categorie_id')
    stock_faible = request.args.get('stock_faible')
    
    query = Produit.query.filter_by(actif=True)
    
    if search:
        query = query.filter(or_(
            Produit.nom.ilike(f'%{search}%'),
            Produit.reference.ilike(f'%{search}%'),
            Produit.code_barre.ilike(f'%{search}%')
        ))
    
    if categorie_id:
        query = query.filter_by(categorie_id=categorie_id)
    
    if stock_faible == 'true':
        query = query.filter(Produit.stock_actuel <= Produit.stock_min)
    
    produits = query.all()
    return jsonify([p.to_dict() for p in produits])

@app.route('/api/produits', methods=['POST'])
@login_required
def create_produit():
    data = request.json
    
    # Vérifier si la référence existe
    if Produit.query.filter_by(reference=data['reference']).first():
        return jsonify({'error': 'Référence déjà utilisée'}), 400
    
    produit = Produit(
        nom=data['nom'],
        reference=data['reference'],
        code_barre=data.get('code_barre'),
        description=data.get('description'),
        prix_achat=data['prix_achat'],
        prix_vente=data['prix_vente'],
        tva=data.get('tva', 0),
        stock_actuel=data.get('stock_actuel', 0),
        stock_min=data.get('stock_min', 0),
        stock_max=data.get('stock_max', 1000),
        categorie_id=data.get('categorie_id'),
        fournisseur_id=data.get('fournisseur_id'),
        unite_mesure=data.get('unite_mesure', 'unité'),
        emplacement=data.get('emplacement')
    )
    
    db.session.add(produit)
    db.session.commit()
    
    # Créer mouvement initial
    if produit.stock_actuel > 0:
        mouvement = MouvementStock(
            produit_id=produit.id,
            type_mouvement='entrée',
            quantite=produit.stock_actuel,
            quantite_avant=0,
            quantite_apres=produit.stock_actuel,
            motif='Stock initial',
            utilisateur=current_user.username
        )
        db.session.add(mouvement)
        db.session.commit()
    
    return jsonify(produit.to_dict()), 201

@app.route('/api/produits/<int:id>', methods=['PUT'])
@login_required
def update_produit(id):
    produit = Produit.query.get_or_404(id)
    data = request.json
    
    stock_avant = produit.stock_actuel
    
    for key, value in data.items():
        if hasattr(produit, key) and key != 'id':
            setattr(produit, key, value)
    
    # Si le stock a changé, créer un mouvement
    if 'stock_actuel' in data and data['stock_actuel'] != stock_avant:
        mouvement = MouvementStock(
            produit_id=produit.id,
            type_mouvement='ajustement',
            quantite=abs(data['stock_actuel'] - stock_avant),
            quantite_avant=stock_avant,
            quantite_apres=data['stock_actuel'],
            motif='Ajustement manuel',
            utilisateur=current_user.username
        )
        db.session.add(mouvement)
    
    db.session.commit()
    return jsonify(produit.to_dict())

@app.route('/api/produits/<int:id>', methods=['DELETE'])
@login_required
def delete_produit(id):
    produit = Produit.query.get_or_404(id)
    produit.actif = False
    db.session.commit()
    return jsonify({'message': 'Produit désactivé'}), 200

# ==================== ROUTES VENTES ====================

@app.route('/ventes')
@login_required
def ventes():
    return render_template('ventes.html')

@app.route('/api/ventes', methods=['GET'])
@login_required
def get_ventes():
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    client_id = request.args.get('client_id')
    statut = request.args.get('statut')
    
    query = Vente.query
    
    if date_debut:
        query = query.filter(Vente.date_vente >= datetime.fromisoformat(date_debut))
    if date_fin:
        query = query.filter(Vente.date_vente <= datetime.fromisoformat(date_fin))
    if client_id:
        query = query.filter_by(client_id=client_id)
    if statut:
        query = query.filter_by(statut=statut)
    
    ventes = query.order_by(Vente.date_vente.desc()).limit(100).all()
    return jsonify([v.to_dict() for v in ventes])

@app.route('/api/ventes', methods=['POST'])
@login_required
def create_vente():
    data = request.json
    
    produit = Produit.query.get_or_404(data['produit_id'])
    
    if produit.stock_actuel < data['quantite']:
        return jsonify({'error': 'Stock insuffisant'}), 400
    
    # Génération du numéro de facture
    last_vente = Vente.query.order_by(Vente.id.desc()).first()
    next_id = last_vente.id + 1 if last_vente else 1
    numero = f"F{datetime.now().strftime('%Y%m')}{next_id:05d}"
    
    # Calculs
    prix_unitaire = float(data.get('prix_unitaire', produit.prix_vente))
    remise = float(data.get('remise', 0))
    tva = float(data.get('tva', produit.tva))
    
    # Calcul correct du montant avec remise et TVA
    montant_ht = data['quantite'] * prix_unitaire
    montant_remise = montant_ht * (remise/100)
    montant_ht_apres_remise = montant_ht - montant_remise
    montant_tva = montant_ht_apres_remise * (tva/100)
    montant_total = montant_ht_apres_remise + montant_tva
    
    vente = Vente(
        numero_facture=numero,
        produit_id=data['produit_id'],
        client_id=data.get('client_id'),
        user_id=current_user.id,
        quantite=data['quantite'],
        prix_unitaire=prix_unitaire,
        remise=remise,
        tva=tva,
        montant_total=montant_total,
        devise=data.get('devise', app.config['DEFAULT_CURRENCY']),
        mode_paiement=data.get('mode_paiement', 'espèces'),
        statut_paiement=data.get('statut_paiement', 'payé'),
        notes=data.get('notes')
    )
    
    # Mise à jour du stock
    produit.stock_actuel -= data['quantite']
    
    # Enregistrement du mouvement
    mouvement = MouvementStock(
        produit_id=data['produit_id'],
        type_mouvement='sortie',
        quantite=data['quantite'],
        quantite_avant=produit.stock_actuel + data['quantite'],
        quantite_apres=produit.stock_actuel,
        motif=f"Vente {numero}",
        cout_unitaire=prix_unitaire,
        reference_document=numero,
        utilisateur=current_user.username
    )
    
    db.session.add(vente)
    db.session.add(mouvement)
    
    # Enregistrer le paiement si payé
    if vente.statut_paiement == 'payé':
        paiement = Paiement(
            vente_id=vente.id,
            montant=montant_total,
            mode_paiement=vente.mode_paiement,
            reference=numero
        )
        db.session.add(paiement)
    
    db.session.commit()
    
    # Vérifier stock faible
    if produit.stock_faible:
        envoyer_notification(
            current_user.id,
            'stock_faible',
            'Alerte Stock',
            f"Le produit {produit.nom} est en stock faible ({produit.stock_actuel} unités)"
        )
    
    # Envoyer email/SMS au client si configuré
    if vente.client and vente.client.email:
        envoyer_email(
            vente.client.email,
            f"Confirmation de vente - {numero}",
            f"Merci pour votre achat. Facture {numero} - Montant: {montant_total} {vente.devise}"
        )
    
    return jsonify(vente.to_dict()), 201

# ==================== ROUTES COMMANDES FOURNISSEURS ====================

@app.route('/commandes')
@login_required
def commandes():
    return render_template('commandes.html')

@app.route('/api/commandes', methods=['GET'])
@login_required
def get_commandes():
    statut = request.args.get('statut')
    fournisseur_id = request.args.get('fournisseur_id')
    
    query = Commande.query
    
    if statut:
        query = query.filter_by(statut=statut)
    if fournisseur_id:
        query = query.filter_by(fournisseur_id=fournisseur_id)
    
    commandes = query.order_by(Commande.date_commande.desc()).all()
    return jsonify([c.to_dict() for c in commandes])

@app.route('/api/commandes', methods=['POST'])
@login_required
def create_commande():
    data = request.json
    
    # Génération du numéro de commande
    last_cmd = Commande.query.order_by(Commande.id.desc()).first()
    next_id = last_cmd.id + 1 if last_cmd else 1
    numero = f"CMD{datetime.now().strftime('%Y%m')}{next_id:05d}"
    
    commande = Commande(
        numero_commande=numero,
        fournisseur_id=data['fournisseur_id'],
        user_id=current_user.id,
        date_livraison_prevue=datetime.fromisoformat(data['date_livraison_prevue']) if data.get('date_livraison_prevue') else None,
        montant_total=0,
        devise=data.get('devise', app.config['DEFAULT_CURRENCY']),
        mode_paiement=data.get('mode_paiement'),
        notes=data.get('notes')
    )
    
    db.session.add(commande)
    db.session.flush()
    
    # Ajouter les items
    montant_total = 0
    for item_data in data['items']:
        item = CommandeItem(
            commande_id=commande.id,
            produit_id=item_data['produit_id'],
            quantite_commandee=item_data['quantite'],
            prix_unitaire=item_data['prix_unitaire'],
            montant_total=item_data['quantite'] * item_data['prix_unitaire']
        )
        montant_total += item.montant_total
        db.session.add(item)
    
    commande.montant_total = montant_total
    db.session.commit()
    
    # Notifier
    envoyer_notification(
        current_user.id,
        'commande',
        'Nouvelle commande',
        f"Commande {numero} créée - Montant: {montant_total} {commande.devise}"
    )
    
    return jsonify(commande.to_dict()), 201

@app.route('/api/commandes/<int:id>/recevoir', methods=['POST'])
@login_required
def recevoir_commande(id):
    commande = Commande.query.get_or_404(id)
    data = request.json
    
    commande.statut = 'reçue'
    commande.date_livraison_reelle = datetime.utcnow()
    
    # Mettre à jour les stocks
    for item_data in data.get('items', []):
        item = CommandeItem.query.get(item_data['id'])
        if item:
            item.quantite_recue = item_data['quantite_recue']
            
            # Mise à jour du stock produit
            produit = item.produit
            stock_avant = produit.stock_actuel
            produit.stock_actuel += item_data['quantite_recue']
            
            # Enregistrer le mouvement
            mouvement = MouvementStock(
                produit_id=produit.id,
                type_mouvement='entrée',
                quantite=item_data['quantite_recue'],
                quantite_avant=stock_avant,
                quantite_apres=produit.stock_actuel,
                motif=f"Réception commande {commande.numero_commande}",
                cout_unitaire=item.prix_unitaire,
                reference_document=commande.numero_commande,
                utilisateur=current_user.username
            )
            db.session.add(mouvement)
    
    db.session.commit()
    
    return jsonify(commande.to_dict())

# ==================== ROUTES CLIENTS ====================

@app.route('/clients')
@login_required
def clients():
    return render_template('clients.html')

@app.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    search = request.args.get('search', '')
    type_client = request.args.get('type')
    
    query = Client.query.filter_by(actif=True)
    
    if search:
        query = query.filter(or_(
            Client.nom.ilike(f'%{search}%'),
            Client.prenom.ilike(f'%{search}%'),
            Client.email.ilike(f'%{search}%'),
            Client.telephone.ilike(f'%{search}%')
        ))
    
    if type_client:
        query = query.filter_by(type_client=type_client)
    
    clients = query.all()
    return jsonify([c.to_dict() for c in clients])

@app.route('/api/clients', methods=['POST'])
@login_required
def create_client():
    data = request.json
    
    client = Client(
        nom=data['nom'],
        prenom=data.get('prenom'),
        entreprise=data.get('entreprise'),
        email=data.get('email'),
        telephone=data.get('telephone'),
        telephone2=data.get('telephone2'),
        adresse=data.get('adresse'),
        ville=data.get('ville'),
        pays=data.get('pays', 'Burkina Faso'),
        type_client=data.get('type_client', 'particulier'),
        remise_defaut=data.get('remise_defaut', 0),
        plafond_credit=data.get('plafond_credit', 0),
        devise_preferee=data.get('devise_preferee', 'XOF'),
        notes=data.get('notes')
    )
    db.session.add(client)
    db.session.commit()
    
    return jsonify(client.to_dict()), 201

@app.route('/api/clients/<int:id>', methods=['PUT'])
@login_required
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json
    
    for key, value in data.items():
        if hasattr(client, key) and key != 'id':
            setattr(client, key, value)
    
    db.session.commit()
    return jsonify(client.to_dict())

# ==================== ROUTES FOURNISSEURS ====================

@app.route('/fournisseurs')
@login_required
def fournisseurs():
    return render_template('fournisseurs.html')

@app.route('/api/fournisseurs', methods=['GET'])
@login_required
def get_fournisseurs():
    fournisseurs = Fournisseur.query.filter_by(actif=True).all()
    return jsonify([f.to_dict() for f in fournisseurs])

@app.route('/api/fournisseurs', methods=['POST'])
@login_required
def create_fournisseur():
    data = request.json
    
    fournisseur = Fournisseur(
        nom=data['nom'],
        contact=data.get('contact'),
        telephone=data.get('telephone'),
        telephone2=data.get('telephone2'),
        email=data.get('email'),
        adresse=data.get('adresse'),
        ville=data.get('ville'),
        pays=data.get('pays', 'Burkina Faso'),
        site_web=data.get('site_web'),
        conditions_paiement=data.get('conditions_paiement'),
        delai_livraison=data.get('delai_livraison'),
        devise_preferee=data.get('devise_preferee', 'XOF'),
        notes=data.get('notes')
    )
    db.session.add(fournisseur)
    db.session.commit()
    
    return jsonify(fournisseur.to_dict()), 201

@app.route('/api/fournisseurs/<int:id>', methods=['PUT'])
@login_required
def update_fournisseur(id):
    fournisseur = Fournisseur.query.get_or_404(id)
    data = request.json
    
    for key, value in data.items():
        if hasattr(fournisseur, key) and key != 'id':
            setattr(fournisseur, key, value)
    
    db.session.commit()
    return jsonify(fournisseur.to_dict())

# ==================== ROUTES PARAMÈTRES ET STATISTIQUES ====================

@app.route('/parametres')
@login_required
def parametres_page():
    """Page des paramètres système"""
    return render_template('parametres.html')

@app.route('/statistiques')
@login_required
def statistiques_page():
    """Page des statistiques"""
    return render_template('statistiques.html')



# ==================== ROUTES STATISTIQUES COMPLÈTES ====================

from flask import jsonify
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta

# ================= STATISTIQUES VENTES =================
@app.route('/api/stats/ventes')
@login_required
def stats_ventes():
    periode = request.args.get('periode', 'mois')
    now = datetime.now()

    if periode == 'jour':
        debut = datetime(now.year, now.month, now.day)
    elif periode == 'semaine':
        debut = now - timedelta(days=now.weekday())  # lundi de la semaine
    elif periode == 'mois':
        debut = datetime(now.year, now.month, 1)
    elif periode == 'annee':
        debut = datetime(now.year, 1, 1)
    else:
        debut = datetime(now.year, now.month, 1)

    ventes = db.session.query(
        func.sum(Vente.montant_total).label('total'),
        func.count(Vente.id).label('nb')
    ).filter(
        Vente.date_vente >= debut,
        Vente.statut == 'confirmée'
    ).first()

    ca_total = ventes.total or 0
    nb_ventes = ventes.nb or 0
    panier_moyen = ca_total / nb_ventes if nb_ventes else 0

    # Évolution jour par jour sur la période
    evolution = []
    jours = (now - debut).days + 1
    for i in range(jours):
        date_i = debut + timedelta(days=i)
        total_i = db.session.query(func.sum(Vente.montant_total)).filter(
            func.date(Vente.date_vente) == date_i.date(),
            Vente.statut == 'confirmée'
        ).scalar() or 0
        evolution.append({"date": date_i.strftime("%d %b"), "montant": total_i})

    # Ventes par catégorie
    ventes_par_categorie = db.session.query(
        Categorie.nom.label('categorie'),
        func.sum(CommandeItem.montant_total).label('total')
    ).join(Produit, Produit.categorie_id == Categorie.id)\
     .join(CommandeItem, CommandeItem.produit_id == Produit.id)\
     .join(Commande, CommandeItem.commande_id == Commande.id)\
     .filter(Commande.statut == 'confirmée', Commande.date_commande >= debut)\
     .group_by(Categorie.nom).all()

    ventes_cat_list = [{"categorie": c.categorie, "total": c.total} for c in ventes_par_categorie]

    # Ventes par mode de paiement
    ventes_par_paiement = db.session.query(
        Commande.mode_paiement,
        func.sum(Commande.montant_total)
    ).filter(
        Commande.statut == 'confirmée',
        Commande.date_commande >= debut
    ).group_by(Commande.mode_paiement).all()

    ventes_paiement_list = [{"mode": p[0], "total": p[1]} for p in ventes_par_paiement]

    return jsonify({
        "ca_total": ca_total,
        "nb_ventes": nb_ventes,
        "panier_moyen": panier_moyen,
        "evolution": evolution,
        "ventes_par_categorie": ventes_cat_list,
        "ventes_par_paiement": ventes_paiement_list
    })


# ================= STATISTIQUES PRODUITS =================
@app.route('/api/stats/produits')
@login_required
def stats_produits():
    top_ventes = db.session.query(
        Produit.id,
        Produit.nom,
        func.sum(CommandeItem.quantite_commandee).label('quantite'),
        func.sum(CommandeItem.montant_total).label('ca')
    ).join(CommandeItem, CommandeItem.produit_id == Produit.id)\
     .join(Commande, CommandeItem.commande_id == Commande.id)\
     .filter(Commande.statut == 'confirmée')\
     .group_by(Produit.id)\
     .order_by(func.sum(CommandeItem.montant_total).desc())\
     .limit(10).all()

    top_ventes_list = [
        {"id": p.id, "nom": p.nom, "quantite": p.quantite, "ca": p.ca}
        for p in top_ventes
    ]

    return jsonify({"top_ventes": top_ventes_list})


# ================= STATISTIQUES CLIENTS =================
@app.route('/api/stats/clients')
@login_required
def stats_clients():
    # Top clients par achats
    top_clients = db.session.query(
        Client.id,
        Client.nom,
        func.count(Vente.id).label('nb_achats'),
        func.sum(Vente.montant_total).label('total')
    ).join(Vente, Vente.client_id == Client.id)\
     .filter(Vente.statut == 'confirmée')\
     .group_by(Client.id)\
     .order_by(func.sum(Vente.montant_total).desc())\
     .limit(10).all()

    top_clients_list = [
        {"id": c.id, "nom": c.nom, "nb_achats": c.nb_achats, "total": c.total}
        for c in top_clients
    ]

    # Nouveaux clients par mois
    debut_annee = datetime(datetime.now().year, 1, 1)
    nouveaux_par_mois = []
    for i in range(12):
        mois = (debut_annee + timedelta(days=30*i)).month
        annee = (debut_annee + timedelta(days=30*i)).year
        nb = db.session.query(func.count(Client.id)).filter(
            func.extract('month', Client.date_creation) == mois,
            func.extract('year', Client.date_creation) == annee
        ).scalar() or 0
        nouveaux_par_mois.append({"mois": f"{mois}/{annee}", "nombre": nb})

    return jsonify({
        "top_clients": top_clients_list,
        "nouveaux_par_mois": nouveaux_par_mois
    })


# ================= RAPPORT RENTABILITÉ =================
@app.route('/api/rapport/rentabilite')
@login_required
def rapport_rentabilite():
    # Chiffre d'affaires et coût total
    ventes = db.session.query(
        func.sum(Vente.montant_total).label('ca_total'),
        func.sum(Produit.prix_achat * CommandeItem.quantite_commandee).label('cout_total')
    ).join(CommandeItem, CommandeItem.commande_id == Vente.id)\
     .join(Produit, Produit.id == CommandeItem.produit_id)\
     .filter(Vente.statut == 'confirmée').first()

    ca_total = ventes.ca_total or 0
    cout_total = ventes.cout_total or 0
    benefice_brut = ca_total - cout_total
    marge_brute = (benefice_brut / ca_total * 100) if ca_total else 0

    # Top produits rentables
    top_rentables = db.session.query(
        Produit.id,
        Produit.nom,
        func.sum(CommandeItem.quantite_commandee).label('quantite'),
        func.sum(CommandeItem.montant_total).label('ca'),
        func.sum((CommandeItem.montant_total - Produit.prix_achat * CommandeItem.quantite_commandee)).label('benefice'),
        func.sum(Produit.prix_achat * CommandeItem.quantite_commandee).label('cout')
    ).join(CommandeItem, CommandeItem.produit_id == Produit.id)\
     .join(Vente, Vente.id == CommandeItem.commande_id)\
     .filter(Vente.statut == 'confirmée')\
     .group_by(Produit.id)\
     .order_by(func.sum((CommandeItem.montant_total - Produit.prix_achat * CommandeItem.quantite_commandee)).desc())\
     .limit(5).all()

    top_rentables_list = [
        {"id": p.id, "nom": p.nom, "quantite": p.quantite, "ca": p.ca, "benefice": p.benefice, "cout": p.cout}
        for p in top_rentables
    ]

    return jsonify({
        "resume": {
            "ca_total": ca_total,
            "cout_total": cout_total,
            "benefice_brut": benefice_brut,
            "marge_brute": marge_brute
        },
        "top_rentables": top_rentables_list
    })

# ==================== ROUTES NOTIFICATIONS ====================

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.date_creation.desc()).limit(50).all()
    
    return jsonify([n.to_dict() for n in notifications])

@app.route('/api/notifications/<int:id>/lire', methods=['POST'])
@login_required
def marquer_notification_lue(id):
    notif = Notification.query.get_or_404(id)
    notif.lue = True
    db.session.commit()
    return jsonify({'success': True})

# ==================== API CONVERSION DEVISES ====================

@app.route('/api/devise/convertir', methods=['POST'])
@login_required
def convertir_devise_api():
    """Convertit un montant d'une devise à une autre"""
    data = request.json
    montant = data['montant']
    devise_source = data['devise_source']
    devise_cible = data['devise_cible']
    
    montant_converti = convertir_devise_util(montant, devise_source, devise_cible)
    
    return jsonify({
        'montant': montant_converti,
        'montant_source': montant,
        'devise_source': devise_source,
        'montant_cible': montant_converti,
        'devise_cible': devise_cible,
        'taux': app.config['CURRENCIES'][devise_cible]['rate'] / app.config['CURRENCIES'][devise_source]['rate']
    })


# ==================== API GESTION UTILISATEURS ====================

@app.route('/api/users', methods=['GET'])
@login_required
def liste_utilisateurs_api():
    """Retourne la liste des utilisateurs"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
        
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'nom': u.nom,
        'prenom': u.prenom,
        'role': u.role,
        'telephone': u.telephone,
        'actif': u.actif,
        'date_creation': u.date_creation.isoformat() if u.date_creation else None,
        'dernier_login': u.dernier_login.isoformat() if u.dernier_login else None
    } for u in users])

@app.route('/api/users', methods=['POST'])
@login_required
def ajouter_utilisateur_api():
    """Ajoute un nouvel utilisateur"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
        
    data = request.json
    
    # Vérification des données requises
    required_fields = ['username', 'email', 'password', 'nom', 'prenom', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    # Vérification si username/email existe déjà
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Ce nom d\'utilisateur existe déjà'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Cet email existe déjà'}), 400
    
    # Création du nouvel utilisateur
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        nom=data['nom'],
        prenom=data['prenom'],
        role=data['role'],
        telephone=data.get('telephone'),
        actif=True,
        date_creation=datetime.utcnow()
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'id': new_user.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création: ' + str(e)}), 500

@app.route('/api/users/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status_api(id):
    """Active/désactive un utilisateur"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(id)
    
    # Empêcher la désactivation de son propre compte
    if user.id == current_user.id:
        return jsonify({'message': 'Vous ne pouvez pas désactiver votre propre compte'}), 400
    
    user.actif = not user.actif
    db.session.commit()
    
    return jsonify({
        'message': f'Utilisateur {"activé" if user.actif else "désactivé"} avec succès',
        'actif': user.actif

    })


# ==================== GESTION DES ERREURS ====================

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Ressource non trouvée'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Erreur interne du serveur'}), 500

# ==================== INITIALISATION ====================

def init_db():
    """Initialise la base de données avec des données de démonstration"""
    with app.app_context():
        db.create_all()
        
        # Vérifier si des données existent déjà
        if User.query.first() is None:
            # Créer utilisateur admin
            admin = User(
                username='admin',
                email='admin@gestiostock.com',
                nom='Admin',
                prenom='GestioStock',
                role='admin',
                telephone='70000000'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Créer utilisateur standard
            user = User(
                username='vendeur',
                email='vendeur@gestiostock.com',
                nom='Sawadogo',
                prenom='Marie',
                role='user',
                telephone='70111111'
            )
            user.set_password('vendeur123')
            db.session.add(user)
            
            db.session.commit()
            
            # Catégories
            cat_elec = Categorie(nom="Électronique", description="Appareils électroniques et accessoires")
            cat_vete = Categorie(nom="Vêtements", description="Articles vestimentaires")
            cat_alim = Categorie(nom="Alimentation", description="Produits alimentaires")
            db.session.add_all([cat_elec, cat_vete, cat_alim])
            db.session.commit()
            
            # Fournisseurs
            f1 = Fournisseur(
                nom="TechSupply Burkina",
                contact="Ibrahim Sawadogo",
                telephone="70123456",
                email="contact@techsupply.bf",
                adresse="Zone industrielle Kossodo",
                ville="Ouagadougou",
                conditions_paiement="30 jours",
                delai_livraison=7
            )
            f2 = Fournisseur(
                nom="Mode & Style",
                contact="Aminata Ouédraogo",
                telephone="75654321",
                email="info@modestyle.bf",
                adresse="Avenue Kwamé N'Krumah",
                ville="Ouagadougou",
                conditions_paiement="Comptant",
                delai_livraison=3
            )
            db.session.add_all([f1, f2])
            db.session.commit()
            
            # Produits
            p1 = Produit(
                nom="Ordinateur Portable HP",
                reference="ORD-HP-001",
                code_barre="3760123456789",
                description="HP 15.6\" Intel Core i5, 8GB RAM, 256GB SSD",
                prix_achat=350000,
                prix_vente=450000,
                tva=0,
                stock_actuel=12,
                stock_min=3,
                stock_max=30,
                categorie_id=cat_elec.id,
                fournisseur_id=f1.id,
                unite_mesure="unité",
                emplacement="Rayon A-1"
            )
            
            p2 = Produit(
                nom="Smartphone Samsung Galaxy A54",
                reference="TEL-SAM-A54",
                code_barre="8806094123456",
                description="6.4\" AMOLED, 128GB, Triple caméra",
                prix_achat=180000,
                prix_vente=250000,
                tva=0,
                stock_actuel=25,
                stock_min=5,
                stock_max=50,
                categorie_id=cat_elec.id,
                fournisseur_id=f1.id,
                unite_mesure="unité",
                emplacement="Rayon A-2"
            )
            
            p3 = Produit(
                nom="T-shirt Coton Premium",
                reference="TSH-COT-001",
                code_barre="3250123456789",
                description="100% Coton, plusieurs couleurs disponibles",
                prix_achat=3500,
                prix_vente=7500,
                tva=0,
                stock_actuel=150,
                stock_min=20,
                stock_max=300,
                categorie_id=cat_vete.id,
                fournisseur_id=f2.id,
                unite_mesure="pièce",
                emplacement="Rayon B-1"
            )
            
            p4 = Produit(
                nom="Jean Slim Fit",
                reference="JEAN-SLIM-001",
                code_barre="3250123456790",
                description="Jean stretch confortable, tailles 36-44",
                prix_achat=8000,
                prix_vente=15000,
                tva=0,
                stock_actuel=80,
                stock_min=15,
                stock_max=150,
                categorie_id=cat_vete.id,
                fournisseur_id=f2.id,
                unite_mesure="pièce",
                emplacement="Rayon B-2"
            )
            
            db.session.add_all([p1, p2, p3, p4])
            db.session.commit()
            
            # Clients
            c1 = Client(
                nom="Ouédraogo",
                prenom="Jean",
                email="jean.ouedraogo@example.com",
                telephone="70123456",
                adresse="Secteur 15, Ouaga 2000",
                ville="Ouagadougou",
                type_client="particulier",
                remise_defaut=0
            )
            
            c2 = Client(
                nom="Kaboré",
                prenom="Marie",
                entreprise="Entreprise ABC SARL",
                email="marie.kabore@abc.bf",
                telephone="75654321",
                adresse="Zone commerciale centrale",
                ville="Ouagadougou",
                type_client="professionnel",
                remise_defaut=5,
                plafond_credit=1000000
            )
            
            c3 = Client(
                nom="Sawadogo",
                prenom="Paul",
                email="paul.sawadogo@example.com",
                telephone="76888999",
                adresse="Secteur 30",
                ville="Ouagadougou",
                type_client="particulier"
            )
            
            db.session.add_all([c1, c2, c3])
            db.session.commit()
            
            # Paramètres système
            params = [
                ParametreSysteme(cle='nom_entreprise', valeur='GestioStock SARL', type_valeur='string', description='Nom de l\'entreprise'),
                ParametreSysteme(cle='adresse_entreprise', valeur='Ouagadougou, Burkina Faso', type_valeur='string', description='Adresse'),
                ParametreSysteme(cle='telephone_entreprise', valeur='70000000', type_valeur='string', description='Téléphone'),
                ParametreSysteme(cle='email_entreprise', valeur='contact@gestiostock.bf', type_valeur='string', description='Email'),
                ParametreSysteme(cle='tva_defaut', valeur='18', type_valeur='number', description='TVA par défaut (%)'),
                ParametreSysteme(cle='alerte_stock_actif', valeur='true', type_valeur='boolean', description='Activer alertes stock'),
                ParametreSysteme(cle='devise_principale', valeur='XOF', type_valeur='string', description='Devise principale')
            ]
            
            for param in params:
                db.session.add(param)
            
            db.session.commit()
            
            print("✅ Base de données initialisée avec succès!")
            print("👤 Admin: admin / admin123")
            print("👤 Vendeur: vendeur / vendeur123")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)