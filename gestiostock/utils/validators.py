"""
Fonctions de validation
"""
import re

def valider_email(email):
    """Valide une adresse email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def valider_telephone(telephone):
    """Valide un numéro de téléphone (format international simplifié)"""
    # Accepte les formats: +226 XX XX XX XX, 00226 XX XX XX XX, XX XX XX XX
    pattern = r'^(\+226|00226)?\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2}$'
    return re.match(pattern, telephone.replace(' ', '')) is not None

def valider_reference_produit(reference):
    """Valide une référence produit"""
    # Doit contenir seulement des lettres, chiffres et tirets
    pattern = r'^[A-Za-z0-9\-_]+$'
    return re.match(pattern, reference) is not None and len(reference) >= 3

def valider_prix(prix):
    """Valide un prix (positif)"""
    try:
        return float(prix) >= 0
    except (ValueError, TypeError):
        return False