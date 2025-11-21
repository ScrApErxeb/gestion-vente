from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Vente, Produit, Client, MouvementStock, db
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


@ventes_bp.route('/api/ventes', methods=['POST'])
@login_required
def create_vente():
    try:
        data = request.json
        print(f"🛒 Données création vente: {data}")
        
        # Validation
        required_fields = ['produit_id', 'quantite', 'prix_unitaire']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérifier le produit
        produit = Produit.query.get(data['produit_id'])
        if not produit:
            return jsonify({'error': 'Produit non trouvé'}), 404
            
        # Vérifier le stock
        quantite = int(data['quantite'])
        if produit.stock_actuel < quantite:
            return jsonify({'error': f'Stock insuffisant. Disponible: {produit.stock_actuel}, Demandé: {quantite}'}), 400
        
        # Générer numéro de facture
        numero_facture = f"FACT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Calculer le montant total
        sous_total = float(data['prix_unitaire']) * quantite
        remise_montant = sous_total * (float(data.get('remise', 0)) / 100)
        montant_total = sous_total - remise_montant
        
        # Créer la vente
        vente = Vente(
            numero_facture=numero_facture,
            produit_id=data['produit_id'],
            client_id=data.get('client_id'),
            quantite=quantite,
            prix_unitaire=float(data['prix_unitaire']),
            remise=float(data.get('remise', 0)),
            montant_total=montant_total,
            mode_paiement=data.get('mode_paiement', 'espèces'),
            devise=data.get('devise', 'XOF'),
            statut='confirmée',
            statut_paiement='payé',
            notes=data.get('notes'),
            date_vente=datetime.now()
        )
        
        # Mettre à jour le stock
        stock_avant = produit.stock_actuel
        produit.stock_actuel -= quantite
        
        # Créer mouvement de stock
        mouvement = MouvementStock(
            produit_id=produit.id,
            type_mouvement='sortie',
            quantite=quantite,
            quantite_avant=stock_avant,
            quantite_apres=produit.stock_actuel,
            motif=f'Vente {numero_facture}',
            utilisateur=current_user.username
        )
        
        db.session.add(vente)
        db.session.add(mouvement)
        db.session.commit()
        
        # Retourner la vente créée
        vente_data = {
            'id': vente.id,
            'numero_facture': vente.numero_facture,
            'produit': produit.nom,
            'quantite': quantite,
            'montant_total': montant_total,
            'message': 'Vente créée avec succès'
        }
        
        print(f"✅ Vente créée: {numero_facture}")
        return jsonify(vente_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur create_vente: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@ventes_bp.route('/api/ventes/<int:id>/annuler', methods=['PUT'])
@login_required
def annuler_vente(id):
    try:
        vente = Vente.query.get_or_404(id)
        
        if vente.statut == 'annulée':
            return jsonify({'error': 'Vente déjà annulée'}), 400
        
        # Restaurer le stock
        produit = vente.produit
        if produit:
            stock_avant = produit.stock_actuel
            produit.stock_actuel += vente.quantite
            
            # Créer mouvement de stock d'annulation
            mouvement = MouvementStock(
                produit_id=produit.id,
                type_mouvement='entrée',
                quantite=vente.quantite,
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