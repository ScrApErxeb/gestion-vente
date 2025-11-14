from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from sqlalchemy import or_
from models import Client, db

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/clients')
@login_required
def clients_page():
    return render_template('clients.html')

@clients_bp.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    search = request.args.get('search', '')
    type_client = request.args.get('type')
    
    query = Client.query.filter_by(actif=True)
    
    if search:
        query = query.filter(or_(
            Client.nom.ilike(f'%{search}%'),
            Client.prenom.ilike(f'%{search}%'),
            Client.email.ilike(f'%{search}%'),
            Client.telephone.ilike(f'%{search}%')
        ))
    
    if type_client:
        query = query.filter_by(type_client=type_client)
    
    clients = query.all()
    return jsonify([c.to_dict() for c in clients])

@clients_bp.route('/api/clients', methods=['POST'])
@login_required
def create_client():
    data = request.json
    
    client = Client(
        nom=data['nom'],
        prenom=data.get('prenom'),
        entreprise=data.get('entreprise'),
        email=data.get('email'),
        telephone=data.get('telephone'),
        telephone2=data.get('telephone2'),
        adresse=data.get('adresse'),
        ville=data.get('ville'),
        pays=data.get('pays', 'Burkina Faso'),
        type_client=data.get('type_client', 'particulier'),
        remise_defaut=data.get('remise_defaut', 0),
        plafond_credit=data.get('plafond_credit', 0),
        devise_preferee=data.get('devise_preferee', 'XOF'),
        notes=data.get('notes')
    )
    db.session.add(client)
    db.session.commit()
    
    return jsonify(client.to_dict()), 201

@clients_bp.route('/api/clients/<int:id>', methods=['PUT'])
@login_required
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json
    
    for key, value in data.items():
        if hasattr(client, key) and key != 'id':
            setattr(client, key, value)
    
    db.session.commit()
    return jsonify(client.to_dict())