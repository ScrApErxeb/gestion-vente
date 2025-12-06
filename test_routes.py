#!/usr/bin/env python
"""
Script de test pour vérifier que toutes les routes API sont correctement définies
"""

import sys
import os

# Ajouter le répertoire à sys.path pour les imports
sys.path.insert(0, os.path.dirname(__file__))

def check_routes():
    """Vérifier que toutes les routes existent"""
    from gestiostock.routes import api as api_module
    
    routes_to_check = [
        '/api/export/all-data',
        '/api/export/backup', 
        '/api/notifications/nettoyer',
    ]
    
    print("🔍 Vérification des routes API...\n")
    
    found_routes = []
    for route in api_module.api_bp.decos:
        for rule in route:
            if hasattr(rule, 'rule'):
                found_routes.append(rule.rule)
    
    print(f"Total de routes trouvées: {len(found_routes)}\n")
    
    all_ok = True
    for route in routes_to_check:
        found = any(route in r for r in found_routes)
        status = "✅" if found else "❌"
        print(f"{status} {route}")
        if not found:
            all_ok = False
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ TOUS LES TESTS PASSÉS - Routes correctement définies!")
    else:
        print("❌ CERTAINES ROUTES MANQUENT")
    print("="*50)
    
    return all_ok

if __name__ == '__main__':
    try:
        check_routes()
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()
