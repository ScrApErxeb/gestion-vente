"""
Routes API supplémentaires
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from models import Notification, User, db, Vente
from utils.export import exporter_ventes_pdf, exporter_produits_excel
from utils.helpers import convertir_devise, get_system_parameter, set_system_parameter
from datetime import datetime, timedelta
import pandas as pd
import openpyxl
from io import BytesIO

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.date_creation.desc()).limit(50).all()
    
    return jsonify([n.to_dict() for n in notifications])

@api_bp.route('/api/notifications/<int:id>/lire', methods=['POST'])
@login_required
def marquer_notification_lue(id):
    notif = Notification.query.get_or_404(id)
    notif.lue = True
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/api/notifications/marquer-toutes-lues', methods=['POST'])
@login_required
def marquer_toutes_notifications_lues():
    Notification.query.filter_by(
        user_id=current_user.id,
        lue=False
    ).update({'lue': True})
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/api/devise/convertir', methods=['POST'])
@login_required
def convertir_devise_api():
    """Convertit un montant d'une devise à une autre"""
    data = request.json
    montant = data['montant']
    devise_source = data['devise_source']
    devise_cible = data['devise_cible']
    
    from utils.helpers import convertir_devise
    montant_converti = convertir_devise(montant, devise_source, devise_cible)
    
    return jsonify({
        'montant': montant_converti,
        'montant_source': montant,
        'devise_source': devise_source,
        'montant_cible': montant_converti,
        'devise_cible': devise_cible
    })

@api_bp.route('/api/export/ventes/pdf')
@login_required
def export_ventes_pdf():
    """Exporte les ventes en PDF"""
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    query = Vente.query.filter_by(statut='confirmée')
    
    if date_debut:
        query = query.filter(Vente.date_vente >= datetime.fromisoformat(date_debut))
    if date_fin:
        query = query.filter(Vente.date_vente <= datetime.fromisoformat(date_fin))
    
    ventes = query.order_by(Vente.date_vente.desc()).all()
    pdf_buffer = exporter_ventes_pdf(ventes)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'ventes_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
        mimetype='application/pdf'
    )

@api_bp.route('/api/export/produits/excel')
@login_required
def export_produits_excel():
    """Exporte les produits en Excel"""
    from models import Produit
    
    produits = Produit.query.filter_by(actif=True).all()
    excel_buffer = exporter_produits_excel(produits)
    
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=f'produits_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@api_bp.route('/api/users', methods=['GET'])
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

@api_bp.route('/api/system/parametres', methods=['GET'])
@login_required
def get_parametres_systeme():
    """Récupère les paramètres système"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
        
    from models.parametre_systeme import ParametreSysteme
    parametres = ParametreSysteme.query.all()
    
    return jsonify([{
        'cle': p.cle,
        'valeur': p.valeur,
        'description': p.description,
        'type_valeur': p.type_valeur
    } for p in parametres])

@api_bp.route('/api/system/parametres', methods=['POST'])
@login_required
def set_parametres_systeme():
    """Définit les paramètres système"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
        
    data = request.json
    
    for param in data:
        set_system_parameter(
            param['cle'],
            param['valeur'],
            param.get('type_valeur', 'string')
        )
    
    return jsonify({'success': True})

@api_bp.route('/api/users', methods=['POST'])
@login_required
def ajouter_utilisateur_api():
    """Ajoute un nouvel utilisateur"""
    try:
        # Vérifier les permissions
        if current_user.role != 'admin':
            return jsonify({'message': 'Accès non autorisé'}), 403
            
        data = request.json
        print(f"📝 Données création utilisateur: {data}")
        
        # Vérification des données requises
        required_fields = ['username', 'email', 'password', 'nom', 'prenom', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
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
            nom=data['nom'],
            prenom=data['prenom'],
            role=data['role'],
            telephone=data.get('telephone'),
            actif=data.get('actif', True)
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ Utilisateur créé: {new_user.username}")
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur création utilisateur: {e}")
        return jsonify({'message': 'Erreur lors de la création: ' + str(e)}), 500

@api_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    try:
        user = User.query.get_or_404(user_id)
        user.actif = not user.actif
        db.session.commit()
        
        return jsonify({
            'message': f'Utilisateur {"activé" if user.actif else "désactivé"} avec succès',
            'user_id': user.id,
            'is_active': user.actif,
            'username': user.username
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/export/ventes/excel', methods=['GET'])
@login_required
def export_ventes_excel_route():
    """Exporte les ventes en Excel (version simplifiée)"""
    try:
        # Récupérer les paramètres de date
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Valider les paramètres
        if not date_debut or not date_fin:
            return jsonify({'error': 'Les paramètres date_debut et date_fin sont requis'}), 400
        
        # Convertir les dates
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
            date_fin_obj = date_fin_obj + timedelta(days=1)
        except ValueError:
            return jsonify({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}), 400
        
        print(f"🔍 Recherche ventes du {date_debut} au {date_fin}")
        
        # Récupérer les ventes dans la période
        ventes = Vente.query.filter(
            Vente.date_vente >= date_debut_obj,
            Vente.date_vente < date_fin_obj
        ).all()
        
        print(f"📊 {len(ventes)} ventes trouvées")
        
        if not ventes:
            data = [{
                'Message': f'Aucune vente trouvée pour la période du {date_debut} au {date_fin}'
            }]
        else:
            data = []
            for vente in ventes:
                vente_data = vente.to_dict()
                data.append({
                    'ID': vente.id,
                    'Numéro Facture': vente.numero_facture,
                    'Date': vente.date_vente.strftime('%Y-%m-%d %H:%M') if vente.date_vente else '',
                    'Client': vente_data.get('client', 'Client anonyme'),
                    'Produit': vente_data.get('produit', 'Produit inconnu'),
                    'Quantité': vente.quantite,
                    'Prix Unitaire': f"{vente.prix_unitaire:.2f}",
                    'Remise': f"{vente.remise:.2f}",
                    'Montant Total': f"{vente.montant_total:.2f}",
                    'Devise': vente.devise,
                    'Mode Paiement': vente.mode_paiement,
                    'Statut': vente.statut,
                    'Statut Paiement': vente.statut_paiement
                })
        
        # Créer le DataFrame et le fichier Excel
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ventes', index=False)
            
            # Ajuster automatiquement la largeur des colonnes
            worksheet = writer.sheets['Ventes']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        filename = f"ventes_{date_debut}_a_{date_fin}.xlsx"
        print(f"✅ Export Excel réussi: {filename}")
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Erreur export Excel: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500
    

@api_bp.route('/api/export/ventes/preview', methods=['GET'])
@login_required
def preview_ventes_export():
    """Aperçu des données qui seront exportées"""
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        if not date_debut or not date_fin:
            return jsonify({'error': 'Les paramètres date_debut et date_fin sont requis'}), 400
        
        # Même logique de récupération que l'export
        from models.produit import Produit
        from models.client import Client
        
        ventes = db.session.query(
            Vente, Produit, Client
        ).join(
            Produit, Vente.produit_id == Produit.id
        ).outerjoin(
            Client, Vente.client_id == Client.id
        ).filter(
            Vente.date_vente >= datetime.strptime(date_debut, '%Y-%m-%d'),
            Vente.date_vente < datetime.strptime(date_fin, '%Y-%m-%d') + timedelta(days=1)
        ).all()
        
        preview_data = []
        for vente, produit, client in ventes[:5]:  # Limiter à 5 pour l'aperçu
            preview_data.append({
                'numero_facture': vente.numero_facture,
                'date': vente.date_vente.strftime('%Y-%m-%d %H:%M'),
                'client': f"{client.nom} {client.prenom}" if client else "Client anonyme",
                'produit': produit.nom,
                'quantite': vente.quantite,
                'montant_total': vente.montant_total
            })
        
        return jsonify({
            'period': f"{date_debut} à {date_fin}",
            'total_ventes': len(ventes),
            'preview': preview_data,
            'export_url': f"/api/export/ventes/excel?date_debut={date_debut}&date_fin={date_fin}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@api_bp.route('/api/export/all-data', methods=['GET'])
@login_required
def export_all_data():
    """Exporte toutes les données de l'application en Excel (multi-feuilles)"""
    try:
        # Vérifier les permissions admin
        if current_user.role != 'admin':
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        print("🔄 Début de l'export de toutes les données...")
        
        # Créer un fichier Excel en mémoire avec plusieurs feuilles
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # === FEUILLE 1: UTILISATEURS ===
            users = User.query.all()
            if users:
                users_data = []
                for user in users:
                    users_data.append({
                        'ID': user.id,
                        'Username': user.username,
                        'Email': user.email,
                        'Nom': user.nom,
                        'Prénom': user.prenom,
                        'Rôle': user.role,
                        'Téléphone': user.telephone or '',
                        'Actif': 'Oui' if user.actif else 'Non',
                        'Date Création': user.date_creation.strftime('%Y-%m-%d %H:%M') if user.date_creation else '',
                        'Dernier Login': user.dernier_login.strftime('%Y-%m-%d %H:%M') if user.dernier_login else ''
                    })
                df_users = pd.DataFrame(users_data)
                df_users.to_excel(writer, sheet_name='Utilisateurs', index=False)
                print(f"✅ {len(users)} utilisateurs exportés")
            
            # === FEUILLE 2: VENTES ===
            ventes = Vente.query.all()
            if ventes:
                ventes_data = []
                for vente in ventes:
                    vente_dict = vente.to_dict()
                    ventes_data.append({
                        'ID': vente.id,
                        'Numéro Facture': vente.numero_facture,
                        'Date': vente.date_vente.strftime('%Y-%m-%d %H:%M') if vente.date_vente else '',
                        'Client': vente_dict.get('client', 'Client anonyme'),
                        'Produit': vente_dict.get('produit', 'Produit inconnu'),
                        'Quantité': vente.quantite,
                        'Prix Unitaire': f"{vente.prix_unitaire:.2f}",
                        'Remise': f"{vente.remise:.2f}",
                        'Montant Total': f"{vente.montant_total:.2f}",
                        'Devise': vente.devise,
                        'Mode Paiement': vente.mode_paiement,
                        'Statut': vente.statut,
                        'Statut Paiement': vente.statut_paiement
                    })
                df_ventes = pd.DataFrame(ventes_data)
                df_ventes.to_excel(writer, sheet_name='Ventes', index=False)
                print(f"✅ {len(ventes)} ventes exportées")
            
            # === FEUILLE 3: PRODUITS ===
            try:
                from models.produit import Produit
                produits = Produit.query.all()
                if produits:
                    produits_data = []
                    for produit in produits:
                        produits_data.append({
                            'ID': produit.id,
                            'Nom': produit.nom,
                            'Description': produit.description or '',
                            'Prix': f"{produit.prix:.2f}" if hasattr(produit, 'prix') else '',
                            'Stock': produit.stock if hasattr(produit, 'stock') else '',
                            'Catégorie': produit.categorie if hasattr(produit, 'categorie') else '',
                            'Actif': 'Oui' if produit.actif else 'Non'
                        })
                    df_produits = pd.DataFrame(produits_data)
                    df_produits.to_excel(writer, sheet_name='Produits', index=False)
                    print(f"✅ {len(produits)} produits exportés")
            except Exception as e:
                print(f"⚠️ Erreur export produits: {e}")
            
            # === FEUILLE 4: CLIENTS ===
            try:
                from models.client import Client
                clients = Client.query.all()
                if clients:
                    clients_data = []
                    for client in clients:
                        clients_data.append({
                            'ID': client.id,
                            'Nom': client.nom,
                            'Prénom': client.prenom,
                            'Email': client.email or '',
                            'Téléphone': client.telephone or '',
                            'Adresse': client.adresse or '',
                            'Entreprise': client.entreprise or '',
                            'Date Inscription': client.date_inscription.strftime('%Y-%m-%d') if hasattr(client, 'date_inscription') and client.date_inscription else ''
                        })
                    df_clients = pd.DataFrame(clients_data)
                    df_clients.to_excel(writer, sheet_name='Clients', index=False)
                    print(f"✅ {len(clients)} clients exportés")
            except Exception as e:
                print(f"⚠️ Erreur export clients: {e}")
            
            # === FEUILLE 5: STATISTIQUES GÉNÉRALES ===
            stats_data = {
                'Statistique': [
                    'Date de génération',
                    'Total Utilisateurs',
                    'Total Ventes', 
                    'Total Produits',
                    'Total Clients',
                    'Chiffre d\'affaires total'
                ],
                'Valeur': [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    len(users),
                    len(ventes),
                    len(produits) if 'produits' in locals() else 'N/A',
                    len(clients) if 'clients' in locals() else 'N/A',
                    f"{sum([v.montant_total for v in ventes]):.2f} XOF" if ventes else '0.00 XOF'
                ]
            }
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Statistiques', index=False)
        
        output.seek(0)
        
        # Nom du fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_complet_{timestamp}.xlsx"
        
        print(f"✅ Export complet réussi: {filename}")
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Erreur export complet: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'export complet: {str(e)}'}), 500
    

@api_bp.route('/api/notifications/nettoyer', methods=['POST'])
@login_required
def nettoyer_notifications():
    """Supprime toutes les notifications lues"""
    try:
        if current_user.role != 'admin':
            return jsonify({'message': 'Accès non autorisé'}), 403
        
        # Compter le nombre de notifications avant suppression
        count_avant = Notification.query.filter_by(user_id=current_user.id).count()
        
        # Supprimer les notifications lues
        Notification.query.filter_by(
            user_id=current_user.id,
            lue=True
        ).delete()
        
        db.session.commit()
        
        # Compter après suppression
        count_apres = Notification.query.filter_by(user_id=current_user.id).count()
        notifications_supprimees = count_avant - count_apres
        
        print(f"🗑️ {notifications_supprimees} notifications nettoyées")
        
        return jsonify({
            'success': True,
            'message': f'{notifications_supprimees} notifications supprimées',
            'notifications_supprimees': notifications_supprimees
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur nettoyage notifications: {e}")
        return jsonify({'error': str(e)}), 500