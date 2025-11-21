from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Fournisseur, db

fournisseurs_bp = Blueprint('fournisseurs', __name__)

@fournisseurs_bp.route('/fournisseurs')
@login_required
def fournisseurs_page():
    return render_template('fournisseurs.html')

@fournisseurs_bp.route('/api/fournisseurs', methods=['GET'])
@login_required
def get_fournisseurs():
    try:
        search = request.args.get('search', '')
        
        query = Fournisseur.query
        
        if search:
            query = query.filter(or_(
                Fournisseur.nom.ilike(f'%{search}%'),
                Fournisseur.contact.ilike(f'%{search}%'),
                Fournisseur.email.ilike(f'%{search}%'),
                Fournisseur.telephone.ilike(f'%{search}%')
            ))
        
        fournisseurs = query.order_by(Fournisseur.nom).all()
        
        fournisseurs_data = []
        for f in fournisseurs:
            fournisseurs_data.append({
                'id': f.id,
                'nom': f.nom,
                'contact': f.contact,
                'telephone': f.telephone,
                'email': f.email,
                'site_web': f.site_web,
                'adresse': f.adresse,
                'ville': f.ville,
                'pays': f.pays,
                'conditions_paiement': f.conditions_paiement,
                'delai_livraison': f.delai_livraison,
                'notes': f.notes,
                'actif': f.actif,
                'date_creation': f.date_creation.isoformat() if f.date_creation else None
            })
        
        return jsonify(fournisseurs_data)
        
    except Exception as e:
        print(f"❌ Erreur get_fournisseurs: {e}")
        return jsonify({'error': str(e)}), 500

@fournisseurs_bp.route('/api/fournisseurs', methods=['POST'])
@login_required
def create_fournisseur():
    try:
        data = request.json
        
        # Validation
        if not data.get('nom') or not data.get('telephone'):
            return jsonify({'error': 'Le nom et le téléphone sont requis'}), 400
        
        # Vérifier si le fournisseur existe déjà
        existing = Fournisseur.query.filter_by(nom=data['nom']).first()
        if existing:
            return jsonify({'error': 'Un fournisseur avec ce nom existe déjà'}), 400
        
        fournisseur = Fournisseur(
            nom=data['nom'],
            contact=data.get('contact'),
            telephone=data['telephone'],
            email=data.get('email'),
            site_web=data.get('site_web'),
            adresse=data.get('adresse'),
            ville=data.get('ville', 'Ouagadougou'),
            pays=data.get('pays', 'Burkina Faso'),
            conditions_paiement=data.get('conditions_paiement'),
            delai_livraison=data.get('delai_livraison'),
            notes=data.get('notes'),
            actif=True
        )
        
        db.session.add(fournisseur)
        db.session.commit()
        
        return jsonify({
            'id': fournisseur.id,
            'nom': fournisseur.nom,
            'message': 'Fournisseur créé avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur create_fournisseur: {e}")
        return jsonify({'error': str(e)}), 500

@fournisseurs_bp.route('/api/fournisseurs/<int:id>', methods=['PUT'])
@login_required
def update_fournisseur(id):
    try:
        fournisseur = Fournisseur.query.get_or_404(id)
        data = request.json
        
        for key, value in data.items():
            if hasattr(fournisseur, key) and key != 'id':
                setattr(fournisseur, key, value)
        
        db.session.commit()
        
        return jsonify({
            'id': fournisseur.id,
            'nom': fournisseur.nom,
            'message': 'Fournisseur modifié avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur update_fournisseur: {e}")
        return jsonify({'error': str(e)}), 500

@fournisseurs_bp.route('/api/fournisseurs/<int:id>/desactiver', methods=['PUT'])
@login_required
def desactiver_fournisseur(id):
    try:
        fournisseur = Fournisseur.query.get_or_404(id)
        fournisseur.actif = False
        db.session.commit()
        
        return jsonify({'message': 'Fournisseur désactivé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur desactiver_fournisseur: {e}")
        return jsonify({'error': str(e)}), 500

@fournisseurs_bp.route('/api/fournisseurs/<int:id>/activer', methods=['PUT'])
@login_required
def activer_fournisseur(id):
    try:
        fournisseur = Fournisseur.query.get_or_404(id)
        fournisseur.actif = True
        db.session.commit()
        
        return jsonify({'message': 'Fournisseur activé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur activer_fournisseur: {e}")
        return jsonify({'error': str(e)}), 500