"""
Gestion des notifications
"""
from models import Notification, User, Produit, db

def envoyer_notification(user_id, type_notif, titre, message):
    """Crée une notification pour un utilisateur"""
    notif = Notification(
        user_id=user_id,
        type=type_notif,
        titre=titre,
        message=message
    )
    db.session.add(notif)
    db.session.commit()
    return notif

def envoyer_notification_globale(type_notif, titre, message, roles=None):
    """Envoie une notification à tous les utilisateurs (ou à des rôles spécifiques)"""
    query = User.query.filter_by(actif=True)
    if roles:
        query = query.filter(User.role.in_(roles))
    
    users = query.all()
    for user in users:
        envoyer_notification(user.id, type_notif, titre, message)
    
    return len(users)

def verifier_stock_faible():
    """Vérifie et envoie des alertes pour les produits en stock faible"""
    produits_faible = Produit.query.filter(
        Produit.stock_actuel <= Produit.stock_min,
        Produit.actif == True
    ).all()
    
    if produits_faible:
        # Notifier les admins et managers
        envoyer_notification_globale(
            'stock_faible',
            'Alerte Stock Faible',
            f"{len(produits_faible)} produit(s) en stock faible nécessitent une attention",
            roles=['admin', 'manager']
        )
    
    return produits_faible

def get_notifications_non_lues(user_id):
    """Récupère les notifications non lues d'un utilisateur"""
    return Notification.query.filter_by(
        user_id=user_id,
        lue=False
    ).order_by(Notification.date_creation.desc()).all()