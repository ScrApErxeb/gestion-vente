from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from models import Fournisseur, db

fournisseurs_bp = Blueprint('fournisseurs', __name__)

@fournisseurs_bp.route('/fournisseurs')
@login_required
def fournisseurs_page():
    return render_template('fournisseurs.html')

@fournisseurs_bp.route('/api/fournisseurs', methods=['GET'])
@login_required
def get_fournisseurs():
    fournisseurs = Fournisseur.query.filter_by(actif=True).all()
    return jsonify([f.to_dict() for f in fournisseurs])

@fournisseurs_bp.route('/api/fournisseurs', methods=['POST'])
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

@fournisseurs_bp.route('/api/fournisseurs/<int:id>', methods=['PUT'])
@login_required
def update_fournisseur(id):
    fournisseur = Fournisseur.query.get_or_404(id)
    data = request.json
    
    for key, value in data.items():
        if hasattr(fournisseur, key) and key != 'id':
            setattr(fournisseur, key, value)
    
    db.session.commit()
    return jsonify(fournisseur.to_dict())