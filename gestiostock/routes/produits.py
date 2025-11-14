from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Produit, Categorie, MouvementStock, db
from datetime import datetime

produits_bp = Blueprint('produits', __name__)

@produits_bp.route('/produits')
@login_required
def produits_page():
    return render_template('produits.html')

@produits_bp.route('/api/produits', methods=['GET'])
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

@produits_bp.route('/api/produits', methods=['POST'])
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

@produits_bp.route('/api/produits/<int:id>', methods=['PUT'])
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

@produits_bp.route('/api/produits/<int:id>', methods=['DELETE'])
@login_required
def delete_produit(id):
    produit = Produit.query.get_or_404(id)
    produit.actif = False
    db.session.commit()
    return jsonify({'message': 'Produit désactivé'}), 200



# === ROUTES CATÉGORIES ===

@produits_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    """Récupère toutes les catégories"""
    try:
        categories = Categorie.query.filter_by(actif=True).all()
        return jsonify([c.to_dict() for c in categories])
    except Exception as e:
        print(f"❌ Erreur dans get_categories: {e}")
        return jsonify({'error': str(e)}), 500

@produits_bp.route('/api/categories', methods=['POST'])
@login_required
def create_categorie():
    """Crée une nouvelle catégorie"""
    try:
        data = request.json
        
        # Validation
        if not data.get('nom'):
            return jsonify({'error': 'Le nom de la catégorie est requis'}), 400
        
        # Vérifier si la catégorie existe déjà
        if Categorie.query.filter_by(nom=data['nom']).first():
            return jsonify({'error': 'Cette catégorie existe déjà'}), 400
        
        categorie = Categorie(
            nom=data['nom'],
            description=data.get('description'),
            parent_id=data.get('parent_id')
        )
        
        db.session.add(categorie)
        db.session.commit()
        
        return jsonify(categorie.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur dans create_categorie: {e}")
        return jsonify({'error': str(e)}), 500

@produits_bp.route('/api/categories/<int:id>', methods=['PUT'])
@login_required
def update_categorie(id):
    """Met à jour une catégorie"""
    try:
        categorie = Categorie.query.get_or_404(id)
        data = request.json
        
        for key, value in data.items():
            if hasattr(categorie, key) and key != 'id':
                setattr(categorie, key, value)
        
        db.session.commit()
        return jsonify(categorie.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur dans update_categorie: {e}")
        return jsonify({'error': str(e)}), 500

@produits_bp.route('/api/categories/<int:id>', methods=['DELETE'])
@login_required
def delete_categorie(id):
    """Désactive une catégorie"""
    try:
        categorie = Categorie.query.get_or_404(id)
        categorie.actif = False
        db.session.commit()
        
        return jsonify({'message': 'Catégorie désactivée'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur dans delete_categorie: {e}")
        return jsonify({'error': str(e)}), 500