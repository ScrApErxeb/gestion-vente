from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import Commande, CommandeItem, MouvementStock, Produit, db
from datetime import datetime
from utils.notifications import envoyer_notification

commandes_bp = Blueprint('commandes', __name__)

@commandes_bp.route('/commandes')
@login_required
def commandes_page():
    return render_template('commandes.html')

@commandes_bp.route('/api/commandes', methods=['GET'])
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

@commandes_bp.route('/api/commandes', methods=['POST'])
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
        devise=data.get('devise', 'XOF'),
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

@commandes_bp.route('/api/commandes/<int:id>/recevoir', methods=['POST'])
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