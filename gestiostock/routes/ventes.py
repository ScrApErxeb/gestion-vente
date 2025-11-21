from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Vente, Produit, Client, MouvementStock, db, VenteItem
from datetime import datetime
import random

ventes_bp = Blueprint('ventes', __name__)

@ventes_bp.route('/ventes')
@login_required
def ventes_page():
    return render_template('ventes.html')


@ventes_bp.route('/api/ventes', methods=['GET'])
@login_required
def get_ventes():
    try:
        print("🔍 Début get_ventes...")
        
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        client_id = request.args.get('client_id')
        statut = request.args.get('statut')
        
        print(f"📅 Filtres - date_debut: {date_debut}, date_fin: {date_fin}")
        
        # Charger les ventes avec leurs relations
        query = Vente.query.options(
            db.joinedload(Vente.produit_vendu),  # ⭐ NOUVEAU NOM
            db.joinedload(Vente.client_acheteur) # ⭐ NOUVEAU NOM
        )
        
        # Filtres
        if date_debut:
            try:
                date_obj = datetime.strptime(date_debut, '%Y-%m-%d')
                query = query.filter(Vente.date_vente >= date_obj)
            except ValueError as e:
                print(f"❌ Erreur format date_debut: {e}")
                return jsonify({'error': 'Format de date début invalide. Utilisez YYYY-MM-DD'}), 400
                
        if date_fin:
            try:
                date_obj = datetime.strptime(date_fin, '%Y-%m-%d')
                date_obj = date_obj.replace(hour=23, minute=59, second=59)
                query = query.filter(Vente.date_vente <= date_obj)
            except ValueError as e:
                print(f"❌ Erreur format date_fin: {e}")
                return jsonify({'error': 'Format de date fin invalide. Utilisez YYYY-MM-DD'}), 400
                
        if client_id:
            query = query.filter(Vente.client_id == client_id)
        if statut:
            query = query.filter(Vente.statut == statut)
        
        ventes = query.order_by(Vente.date_vente.desc()).all()
        print(f"✅ {len(ventes)} ventes trouvées")
        
        # Utilisation de to_dict()
        ventes_data = []
        for v in ventes:
            try:
                vente_dict = v.to_dict()
                ventes_data.append(vente_dict)
            except Exception as e:
                print(f"❌ Erreur to_dict() pour vente {v.id}: {e}")
                # Fallback basique
                ventes_data.append({
                    'id': v.id,
                    'numero_facture': v.numero_facture,
                    'produit': f"Produit ID:{v.produit_id}",
                    'client': "Client anonyme",
                    'quantite': v.quantite,
                    'montant_total': float(v.montant_total) if v.montant_total else 0,
                    'date_vente': v.date_vente.isoformat() if v.date_vente else None,
                    'statut': v.statut
                })
        
        print(f"🎯 {len(ventes_data)} ventes formatées")
        return jsonify(ventes_data)
        
    except Exception as e:
        print(f"❌ Erreur get_ventes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# Exemple Flask / SQLAlchemy
@ventes_bp.route('/ventes', methods=['POST'])
def create_vente():
    data = request.get_json()
    client_id = data.get('client_id')
    devise = data.get('devise', 'XOF')
    mode_paiement = data.get('mode_paiement', 'espèces')
    notes = data.get('notes', '')
    items = data.get('items', [])

    if not items:
        return jsonify({'error': 'Aucun produit dans la vente'}), 400

    vente = Vente(client_id=client_id, devise=devise,
                  mode_paiement=mode_paiement, notes=notes,
                  statut='confirmée', statut_paiement='payé')

    for item in items:
        produit_id = item['produit_id']
        quantite = item['quantite']
        prix_unitaire = item['prix_unitaire']
        remise = item.get('remise', 0)
        venteItem = VenteItem(produit_id=produit_id,
                              quantite=quantite,
                              prix_unitaire=prix_unitaire,
                              remise=remise)
        vente.items_vente.append(venteItem)

    db.session.add(vente)
    db.session.commit()
    return jsonify({'message':'Vente enregistrée','vente_id':vente.id}), 201


@ventes_bp.route('/api/ventes/<int:id>/annuler', methods=['PUT'])
@login_required
def annuler_vente(id):
    try:
        vente = Vente.query.get_or_404(id)
        
        if vente.statut == 'annulée':
            return jsonify({'error': 'Vente déjà annulée'}), 400
        
        # Restaurer le stock pour chaque produit de la vente
        for item in vente.items_vente:
            produit = item.produit_lie
            if produit:
                stock_avant = produit.stock_actuel
                produit.stock_actuel += item.quantite
                
                # Créer mouvement de stock d'annulation
                mouvement = MouvementStock(
                    produit_id=produit.id,
                    type_mouvement='entrée',
                    quantite=item.quantite,
                    quantite_avant=stock_avant,
                    quantite_apres=produit.stock_actuel,
                    motif=f'Annulation vente {vente.numero_facture}',
                    utilisateur=current_user.username
                )
                db.session.add(mouvement)
        
        vente.statut = 'annulée'
        db.session.commit()
        
        return jsonify({'message': 'Vente annulée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur annuler_vente: {e}")
        return jsonify({'error': str(e)}), 500



@ventes_bp.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    try:
        clients = Client.query.filter_by(actif=True).all()
        
        clients_data = []
        for c in clients:
            clients_data.append({
                'id': c.id,
                'nom': c.nom or '',
                'prenom': c.prenom or '',
                'telephone': c.telephone or '',
                'email': c.email or ''
            })
        
        print(f"✅ {len(clients_data)} clients chargés")
        return jsonify(clients_data)
    except Exception as e:
        print(f"❌ Erreur get_clients: {e}")
        return jsonify({'error': str(e)}), 500