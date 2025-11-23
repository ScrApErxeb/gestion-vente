from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Produit, Categorie, MouvementStock, db, Fournisseur  # ✅ Bon import
from datetime import datetime

produits_bp = Blueprint('produits', __name__)

@produits_bp.route('/produits')
@login_required
def produits_page():
    return render_template('produits.html')

# === PRODUITS ===

@produits_bp.route('/api/produits', methods=['GET'])
@login_required
def get_produits():
    try:
        search = request.args.get('search', '')
        categorie_id = request.args.get('categorie_id')
        stock_faible = request.args.get('stock_faible')
        
        # ✅ CORRECTION: Utiliser Produit.query, pas Fournisseur.query
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
        
        # ✅ FORMATAGE MANUEL SANS to_dict()
        produits_data = []
        for p in produits:
            produit_data = {
                'id': p.id,
                'reference': p.reference,
                'code_barre': p.code_barre or '',
                'nom': p.nom,
                'description': p.description or '',
                'prix_achat': float(p.prix_achat),
                'prix_vente': float(p.prix_vente),
                'tva': float(p.tva) if p.tva else 0.0,
                'stock_actuel': p.stock_actuel,
                'stock_min': p.stock_min,
                'stock_max': p.stock_max,
                'unite_mesure': p.unite_mesure or 'unité',
                'emplacement': p.emplacement or '',
                'categorie_id': p.categorie_id,
                'fournisseur_id': p.fournisseur_id,
                'actif': p.actif,
                'valeur_stock': float(p.prix_achat * p.stock_actuel),
                'stock_faible': p.stock_actuel <= p.stock_min
            }
            
            # Ajouter les noms des relations
            if p.categorie:
                produit_data['categorie'] = p.categorie.nom
            else:
                produit_data['categorie'] = None
                
            if p.fournisseur:
                produit_data['fournisseur'] = p.fournisseur.nom
            else:
                produit_data['fournisseur'] = None
                
            produits_data.append(produit_data)
        
        print(f"✅ {len(produits_data)} produits chargés")
        return jsonify(produits_data)
    
    except Exception as e:
        print(f"❌ Erreur get_produits: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# === CATÉGORIES ===



@produits_bp.route('/categories', methods=['POST'])
@login_required
def create_category():
    try:
        data = request.get_json()

        if not data or 'nom' not in data:
            return jsonify({'error': 'Le nom de la catégorie est obligatoire'}), 400

        new_cat = Categorie(
            nom=data['nom'],
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            actif=True
        )

        db.session.add(new_cat)
        db.session.commit()

        return jsonify({
            'id': new_cat.id,
            'nom': new_cat.nom,
            'description': new_cat.description,
            'parent_id': new_cat.parent_id,
            'actif': new_cat.actif
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur create_category: {e}")
        return jsonify({'error': str(e)}), 500


@produits_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    try:
        categories = Categorie.query.filter_by(actif=True).all()
        
        categories_data = []
        for cat in categories:
            categories_data.append({
                'id': cat.id,
                'nom': cat.nom,
                'description': cat.description or '',
                'parent_id': cat.parent_id,
                'actif': cat.actif
            })
        
        print(f"✅ {len(categories_data)} catégories chargées")
        return jsonify(categories_data)
    except Exception as e:
        print(f"❌ Erreur get_categories: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# === CATEGORIES - EDITION ===

@produits_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@login_required
def update_category(cat_id):
    try:
        cat = Categorie.query.get_or_404(cat_id)
        data = request.get_json()

        # Vérifie si le nouveau nom existe ailleurs
        if "nom" in data:
            existing = Categorie.query.filter(
                Categorie.nom == data["nom"],
                Categorie.id != cat_id
            ).first()

            if existing:
                return jsonify({
                    "error": "Une autre catégorie possède déjà ce nom."
                }), 400

            cat.nom = data["nom"]

        cat.description = data.get('description', cat.description)
        cat.parent_id = data.get('parent_id', cat.parent_id)

        db.session.commit()

        return jsonify({
            'id': cat.id,
            'nom': cat.nom,
            'description': cat.description,
            'parent_id': cat.parent_id,
            'actif': cat.actif
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur update_category: {e}")
        return jsonify({'error': str(e)}), 500


# === CATEGORIES - SUPP ===

@produits_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@login_required
def delete_category(cat_id):
    try:
        cat = Categorie.query.get(cat_id)
        if not cat:
            return jsonify({'error': 'Catégorie introuvable'}), 404

        # Soft delete
        cat.actif = False

        db.session.commit()

        return jsonify({'message': 'Catégorie désactivée'})

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur delete_category: {e}")
        return jsonify({'error': str(e)}), 500


# === FOURNISSEURS ===

@produits_bp.route('/api/fournisseurs', methods=['GET'])
@login_required
def get_fournisseurs():
    try:
        fournisseurs = Fournisseur.query.filter_by(actif=True).all()
        
        fournisseurs_data = []
        for f in fournisseurs:
            fournisseurs_data.append({
                'id': f.id,
                'nom': f.nom,
                'email': f.email or '',
                'telephone': f.telephone or '',
                'adresse': f.adresse or ''
            })
        
        print(f"✅ {len(fournisseurs_data)} fournisseurs chargés")
        return jsonify(fournisseurs_data)
    except Exception as e:
        print(f"❌ Erreur get_fournisseurs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# === CRÉATION PRODUIT ===

@produits_bp.route('/api/produits', methods=['POST'])
@login_required
def create_produit():
    try:
        data = request.json
        print(f"📦 Données reçues création produit: {data}")
        
        # Validation des champs requis
        required_fields = ['nom', 'reference', 'prix_achat', 'prix_vente']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérifier si la référence existe
        existing = Produit.query.filter_by(reference=data['reference']).first()
        if existing:
            return jsonify({'error': 'Référence déjà utilisée'}), 400
        
        # Création du produit
        produit = Produit(
            nom=data['nom'],
            reference=data['reference'],
            code_barre=data.get('code_barre'),
            description=data.get('description'),
            prix_achat=float(data['prix_achat']),
            prix_vente=float(data['prix_vente']),
            tva=float(data.get('tva', 0)),
            stock_actuel=int(data.get('stock_actuel', 0)),
            stock_min=int(data.get('stock_min', 0)),
            stock_max=int(data.get('stock_max', 1000)),
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
        
        # Retourner le produit créé
        produit_data = {
            'id': produit.id,
            'reference': produit.reference,
            'nom': produit.nom,
            'prix_achat': float(produit.prix_achat),
            'prix_vente': float(produit.prix_vente),
            'stock_actuel': produit.stock_actuel,
            'message': 'Produit créé avec succès'
        }
        
        print(f"✅ Produit créé: {produit.reference}")
        return jsonify(produit_data), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur create_produit: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# === MODIFICATION PRODUIT ===

@produits_bp.route('/api/produits/<int:id>', methods=['PUT'])
@login_required
def modifier_produit(id):
    produit = Produit.query.get_or_404(id)  # 404 si non trouvé
    try:
        data = request.get_json()

        # Mettre à jour seulement les champs présents dans la requête
        for key in ['reference', 'nom', 'description', 'prix_achat', 'prix_vente',
                    'tva', 'stock_actuel', 'stock_min', 'stock_max',
                    'categorie_id', 'fournisseur_id', 'unite_mesure', 'emplacement', 'code_barre']:
            if key in data:
                setattr(produit, key, data[key])

        db.session.commit()
        return jsonify({'message': 'Produit modifié avec succès', 'produit_id': produit.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# === SUPPRESSION PRODUIT ===

@produits_bp.route('/api/produits/<int:id>', methods=['DELETE'])
@login_required
def delete_produit(id):
    try:
        produit = Produit.query.get_or_404(id)
        produit.actif = False
        db.session.commit()
        
        print(f"✅ Produit {id} désactivé")
        return jsonify({'message': 'Produit désactivé'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur delete_produit: {e}")
        return jsonify({'error': str(e)}), 500