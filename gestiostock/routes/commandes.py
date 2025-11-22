from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Commande, CommandeItem, Fournisseur, Produit, MouvementStock, db
from datetime import datetime
import random

commandes_bp = Blueprint('commandes', __name__)

@commandes_bp.route('/commandes')
@login_required
def commandes_page():
    return render_template('commandes.html')


@commandes_bp.route('/api/commandes', methods=['GET'])
@login_required
def get_commandes():
    try:
        fournisseur_id = request.args.get('fournisseur_id')
        statut = request.args.get('statut')
        
        query = Commande.query
        
        if fournisseur_id:
            query = query.filter(Commande.fournisseur_id == fournisseur_id)
        if statut:
            query = query.filter(Commande.statut == statut)
        
        commandes = query.order_by(Commande.date_commande.desc()).all()
        
        commandes_data = []
        for c in commandes:
            # Récupérer le fournisseur
            fournisseur = Fournisseur.query.get(c.fournisseur_id)
            
            # Construire les données de commande
            commande_data = {
                'id': c.id,
                'numero_commande': c.numero_commande,
                'date_commande': c.date_commande.isoformat() if c.date_commande else None,
                'date_livraison_prevue': c.date_livraison_prevue.isoformat() if c.date_livraison_prevue else None,
                'date_livraison_reelle': c.date_livraison_reelle.isoformat() if c.date_livraison_reelle else None,
                'montant_total': float(c.montant_total) if c.montant_total else 0,
                'mode_paiement': c.mode_paiement,
                'devise': c.devise,
                'statut': c.statut,
                'statut_paiement': c.statut_paiement,
                'notes': c.notes,
                'fournisseur_id': c.fournisseur_id,
                'fournisseur': fournisseur.nom if fournisseur else 'Fournisseur inconnu',
                'nb_items': len(c.items) if hasattr(c, 'items') else 0,
                'items': []
            }
            
            # Ajouter les items de la commande
            if hasattr(c, 'items'):
                for item in c.items:
                    produit_nom = item.produit.nom if hasattr(item, 'produit') and item.produit else f"Produit ID:{item.produit_id}"
                    commande_data['items'].append({
                        'id': item.id,
                        'produit_id': item.produit_id,
                        'produit': produit_nom,
                        'quantite_commandee': item.quantite_commandee,
                        'quantite_recue': item.quantite_recue,
                        'prix_unitaire': float(item.prix_unitaire),
                        'montant_total': float(item.montant_total)
                    })
            
            commandes_data.append(commande_data)
        
        return jsonify(commandes_data)
    
    except Exception as e:
        print(f"❌ Erreur get_commandes: {e}")
        return jsonify({'error': str(e)}), 500
   
    
@commandes_bp.route('/api/commandes', methods=['POST'])
@login_required
def create_commande():
    try:
        data = request.json
        print(f"📋 Données création commande: {data}")
        
        # Validation
        if not data.get('fournisseur_id'):
            return jsonify({'error': 'Le fournisseur est requis'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'Au moins un article est requis'}), 400
        
        # Générer numéro de commande
        numero_commande = f"CMD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Calculer le montant total
        montant_total = sum(item['quantite'] * item['prix_unitaire'] for item in data['items'])
        
        # Créer la commande
        commande = Commande(
            numero_commande=numero_commande,
            fournisseur_id=data['fournisseur_id'],
            date_livraison_prevue=datetime.fromisoformat(data['date_livraison_prevue']) if data.get('date_livraison_prevue') else None,
            montant_total=montant_total,
            mode_paiement=data.get('mode_paiement', 'comptant'),
            devise=data.get('devise', 'XOF'),
            statut='en_attente',
            notes=data.get('notes'),
            date_commande=datetime.now()
        )
        
        db.session.add(commande)
        db.session.flush()  # Pour obtenir l'ID
        
        # ⭐ CORRECTION: Utilisez les bons noms de champs pour CommandeItem
        for item_data in data['items']:
            item = CommandeItem(
                commande_id=commande.id,
                produit_id=item_data['produit_id'],
                quantite_commandee=item_data['quantite'],  # ⭐ CORRECT: quantite_commandee
                prix_unitaire=item_data['prix_unitaire'],
                montant_total=item_data['quantite'] * item_data['prix_unitaire']
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'id': commande.id,
            'numero_commande': commande.numero_commande,
            'montant_total': montant_total,
            'message': 'Commande créée avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur create_commande: {e}")
        return jsonify({'error': str(e)}), 500


@commandes_bp.route('/api/commandes/<int:id>/recevoir', methods=['POST'])
@login_required
def recevoir_commande(id):
    try:
        # ⭐ CORRECTION : Utiliser les NOUVEAUX noms de relations
        commande = Commande.query.options(
            db.joinedload(Commande.items).joinedload(CommandeItem.produit)  # ⭐ produit_lie au lieu de produit_commande
        ).get_or_404(id)
        
        if commande.statut == 'reçue':
            return jsonify({'error': 'Commande déjà réceptionnée'}), 400
        
        print(f"📦 Réception commande {commande.numero_commande} avec {len(commande.items)} articles")
        
        # Mettre à jour les stocks pour chaque item
        for item in commande.items:
            # ⭐ CORRECTION : Utiliser produit_lie (le NOUVEAU nom de relation)
            if hasattr(item, 'produit') and item.produit:
                produit = item.produit
                stock_avant = produit.stock_actuel
                quantite_recue = item.quantite_commandee
                
                # Mettre à jour le stock
                produit.stock_actuel += quantite_recue
                item.quantite_recue = quantite_recue
                
                print(f"  ➕ Produit {produit.nom}: +{quantite_recue} unités (Stock: {stock_avant} → {produit.stock_actuel})")
                
                # Créer mouvement de stock
                mouvement = MouvementStock(
                    produit_id=produit.id,
                    type_mouvement='entrée',
                    quantite=quantite_recue,
                    quantite_avant=stock_avant,
                    quantite_apres=produit.stock_actuel,
                    motif=f'Réception commande {commande.numero_commande}',
                    utilisateur=current_user.username
                )
                db.session.add(mouvement)
            else:
                print(f"  ⚠️ Produit non trouvé pour l'item {item.id}")
        
        # Mettre à jour le statut de la commande
        commande.statut = 'reçue'
        commande.date_livraison_reelle = datetime.now()
        commande.statut_paiement = 'payé'
        
        db.session.commit()
        
        print(f"✅ Commande {commande.numero_commande} réceptionnée avec succès")
        return jsonify({'message': 'Commande réceptionnée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur recevoir_commande: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500





@commandes_bp.route('/api/commandes/<int:id>/annuler', methods=['PUT'])
@login_required
def annuler_commande(id):
    try:
        commande = Commande.query.get_or_404(id)
        
        if commande.statut == 'reçue':
            return jsonify({'error': 'Impossible d\'annuler une commande déjà réceptionnée'}), 400
        
        commande.statut = 'annulée'
        db.session.commit()
        
        return jsonify({'message': 'Commande annulée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur annuler_commande: {e}")
        return jsonify({'error': str(e)}), 500