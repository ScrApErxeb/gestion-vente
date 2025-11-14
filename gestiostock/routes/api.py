"""
Routes API supplémentaires
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from models import Notification, User, db
from utils.export import exporter_ventes_pdf, exporter_produits_excel
from utils.helpers import convertir_devise, get_system_parameter, set_system_parameter
from datetime import datetime, timedelta

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
    from models import Vente
    
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