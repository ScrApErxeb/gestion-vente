"""
Fonctions utilitaires générales
"""
from flask import current_app
from models import db

def convertir_devise(montant, devise_source, devise_cible):
    """Convertit un montant d'une devise à une autre"""
    if devise_source == devise_cible:
        return montant
    
    currencies = current_app.config.get('CURRENCIES', {})
    if devise_source not in currencies or devise_cible not in currencies:
        return montant
    
    # Convertir en devise de base (XOF)
    montant_base = montant / currencies[devise_source]['rate']
    # Convertir en devise cible
    return montant_base * currencies[devise_cible]['rate']

def format_currency(amount, currency='XOF'):
    """Formate un montant en devise"""
    currencies = current_app.config.get('CURRENCIES', {})
    symbol = currencies.get(currency, {}).get('symbol', 'F')
    
    if amount is None:
        amount = 0
        
    return f"{amount:,.0f} {symbol}".replace(',', ' ')

def get_system_parameter(key, default=None):
    """Récupère un paramètre système"""
    from models.parametre_systeme import ParametreSysteme
    return ParametreSysteme.get_value(key, default)

def set_system_parameter(key, value, value_type='string'):
    """Définit un paramètre système"""
    from models.parametre_systeme import ParametreSysteme
    ParametreSysteme.set_value(key, value, value_type)