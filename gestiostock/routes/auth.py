from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    print(f"🔐 REQUÊTE LOGIN - Méthode: {request.method}")
    print(f"📦 Headers: {dict(request.headers)}")
    print(f"🌐 Content-Type: {request.content_type}")
    
    if request.method == 'POST':
        try:
            # Vérifier le Content-Type
            if not request.is_json:
                print("❌ La requête n'est pas en JSON")
                return jsonify({
                    'success': False, 
                    'message': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json(silent=True)
            if not data:
                print("❌ Impossible de parser le JSON")
                return jsonify({
                    'success': False, 
                    'message': 'Données JSON invalides'
                }), 400
                
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            print(f"🔍 Données reçues - Username: '{username}', Password: {'*' * len(password)}")
            
            if not username or not password:
                print("❌ Champs manquants")
                return jsonify({
                    'success': False, 
                    'message': 'Nom d\'utilisateur et mot de passe requis'
                }), 400
            
            # Recherche de l'utilisateur
            user = User.query.filter_by(username=username).first()
            
            if user:
                print(f"✅ Utilisateur trouvé: {user.username} (ID: {user.id})")
                print(f"   📧 Email: {user.email}")
                print(f"   👥 Rôle: {user.role}")
                print(f"   ✅ Actif: {user.actif}")
                print(f"   🔑 Hash présent: {bool(user.password_hash)}")
                
                if not user.actif:
                    print(f"❌ Compte désactivé: {username}")
                    return jsonify({
                        'success': False, 
                        'message': 'Compte désactivé'
                    }), 401
                
                # Vérification du mot de passe
                print(f"🔐 Vérification du mot de passe...")
                password_correct = user.check_password(password)
                print(f"   🔍 Résultat vérification: {password_correct}")
                
                if password_correct:
                    print(f"🎉 Mot de passe correct - Tentative de connexion...")
                    
                    # Tenter la connexion
                    login_success = login_user(user, remember=False)
                    print(f"   🔑 Résultat login_user: {login_success}")
                    
                    if login_success:
                        user.dernier_login = datetime.utcnow()
                        db.session.commit()
                        
                        print(f"🎊 CONNEXION RÉUSSIE pour {user.username}")
                        print(f"   👤 User connecté: {current_user.is_authenticated}")
                        print(f"   🆔 ID utilisateur: {current_user.get_id()}")
                        
                        return jsonify({
                            'success': True, 
                            'user': user.to_dict(),
                            'redirect': '/dashboard'
                        })
                    else:
                        print(f"❌ Échec de login_user()")
                        return jsonify({
                            'success': False, 
                            'message': 'Erreur lors de la connexion'
                        }), 500
                else:
                    print(f"❌ Mot de passe incorrect pour {username}")
                    return jsonify({
                        'success': False, 
                        'message': 'Nom d\'utilisateur ou mot de passe incorrect'
                    }), 401
            else:
                print(f"❌ Utilisateur non trouvé: {username}")
                return jsonify({
                    'success': False, 
                    'message': 'Nom d\'utilisateur ou mot de passe incorrect'
                }), 401
                
        except Exception as e:
            print(f"💥 ERREUR CRITIQUE lors de la connexion: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'message': 'Erreur serveur lors de la connexion'
            }), 500
    
    # GET request - afficher la page de connexion
    if current_user.is_authenticated:
        print(f"🔁 Utilisateur déjà connecté: {current_user.username} - Redirection...")
        return redirect('/')
    
    print("📄 Affichage de la page de connexion")
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    print(f"🚪 Déconnexion de {current_user.username}")
    logout_user()
    return redirect(url_for('auth.login', logout='true'))

@auth_bp.route('/api/auth/status')
def auth_status():
    """API pour vérifier le statut d'authentification"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user': current_user.to_dict() if current_user.is_authenticated else None
    })

@auth_bp.route('/debug/session')
def debug_session():
    """Route de débogage des sessions"""
    from flask import session
    return jsonify({
        'session': dict(session),
        'current_user': current_user.to_dict() if current_user.is_authenticated else None,
        'is_authenticated': current_user.is_authenticated
    })