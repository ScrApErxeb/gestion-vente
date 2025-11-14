from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import Vente, Produit, Paiement, MouvementStock, db
from datetime import datetime
from utils.notifications import envoyer_notification, verifier_stock_faible

ventes_bp = Blueprint('ventes', __name__)

@ventes_bp.route('/ventes')
@login_required
def ventes_page():
    return render_template('ventes.html')

@ventes_bp.route('/api/ventes', methods=['GET'])
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

@ventes_bp.route('/api/ventes', methods=['POST'])
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
        devise=data.get('devise', 'XOF'),
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
    
    return jsonify(vente.to_dict()), 201