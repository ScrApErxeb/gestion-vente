import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-cle-secrete-super-securisee-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///gestiostock_pro.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration multi-devises
    CURRENCIES = {
        'XOF': {'symbol': 'F CFA', 'rate': 1.0, 'name': 'Franc CFA'},
        'EUR': {'symbol': '€', 'rate': 656.0, 'name': 'Euro'},
        'USD': {'symbol': '$', 'rate': 610.0, 'name': 'Dollar US'},
        'GBP': {'symbol': '£', 'rate': 765.0, 'name': 'Livre Sterling'}
    }
    DEFAULT_CURRENCY = 'XOF'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}