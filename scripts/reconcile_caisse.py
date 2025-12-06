"""Script de réconciliation de la caisse.

Calcule : solde_caisse = sum(Paiement.montant) - sum(Depense.montant)
et met à jour ParametreSysteme.solde_caisse.

Usage (PowerShell):
    python scripts\reconcile_caisse.py
"""
import os
import sys

# Ensure repository root and package path are on sys.path so imports like
# 'gestiostock' and the app's (absolute) imports such as 'config' resolve.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PKG = os.path.join(ROOT, 'gestiostock')

for p in (ROOT, PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

from gestiostock.app import create_app
try:
    # app.py imports top-level 'models' (not 'gestiostock.models'), so import the
    # same module to reuse the same SQLAlchemy instance.
    from models import db, Paiement, Depense, ParametreSysteme
except ImportError:
    # Fallback to package import if top-level 'models' isn't available
    from gestiostock.models import db, Paiement, Depense, ParametreSysteme
from sqlalchemy import func


def reconcile():
    app = create_app()
    with app.app_context():
        total_paiements = db.session.query(func.coalesce(func.sum(Paiement.montant), 0)).scalar()
        total_depenses = db.session.query(func.coalesce(func.sum(Depense.montant), 0)).scalar()

        total_paiements = float(total_paiements or 0)
        total_depenses = float(total_depenses or 0)

        solde = total_paiements - total_depenses

        ParametreSysteme.set_value("solde_caisse", solde, type_valeur="number")
        db.session.commit()

        print("Réconciliation terminée :")
        print(f"  total paiements : {total_paiements}")
        print(f"  total dépenses  : {total_depenses}")
        print(f"  solde_caisse mis à jour : {solde}")


if __name__ == '__main__':
    reconcile()
