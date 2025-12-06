"""Backfill des ventes en Paiement + MouvementCaisse.

Usage (PowerShell):
    # preview (no DB writes)
    python scripts\backfill_ventes_payments.py

    # apply (will write to DB) -- make a DB backup before running
    python scripts\backfill_ventes_payments.py --apply

Script behaviour:
 - repère les ventes considérées payées (heuristique: statut_paiement contient 'pay' ou mode_paiement != 'crédit')
 - ignore les ventes qui ont déjà un Paiement lié
 - preview: affiche la liste et les totaux
 - apply: crée un Paiement et un MouvementCaisse par vente, et met à jour ParametreSysteme.solde_caisse
"""
import os
import sys
import argparse
from datetime import datetime

# Ensure imports resolve (same approach as reconcile script)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PKG = os.path.join(ROOT, 'gestiostock')
for p in (ROOT, PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

from gestiostock.app import create_app
try:
    from models import db, Vente, Paiement, MouvementCaisse, ParametreSysteme
except ImportError:
    from gestiostock.models import db, Vente, Paiement, MouvementCaisse, ParametreSysteme


def find_target_ventes():
    # Heuristic: statut_paiement contains 'pay' (payé, payé, paid) OR mode_paiement != 'crédit'
    q = db.session.query(Vente).filter(
        ((Vente.statut_paiement != None) & (Vente.statut_paiement.ilike('%pay%'))) |
        ((Vente.mode_paiement != None) & (Vente.mode_paiement != 'crédit'))
    )
    ventes = q.order_by(Vente.date_vente.asc()).all()

    # filter out ventes that already have a Paiement
    to_backfill = []
    for v in ventes:
        existing = db.session.query(Paiement).filter_by(vente_id=v.id).first()
        if existing:
            continue
        to_backfill.append(v)
    return to_backfill


def preview(app):
    with app.app_context():
        targets = find_target_ventes()
        total = sum(float(v.montant_total or 0) for v in targets)
        print(f"Ventes candidates : {len(targets)}")
        for v in targets:
            print(f"  id={v.id} date={v.date_vente} client={getattr(v.client,'nom',None)} montant={v.montant_total} statut={v.statut_paiement} mode={v.mode_paiement}")
        print(f"Total montant (preview) : {total}")
        return targets, total


def apply_backfill(app, targets):
    with app.app_context():
        # read current solde
        try:
            current = float(ParametreSysteme.get_value('solde_caisse') or 0)
        except Exception:
            current = 0.0

        print(f"Solde caisse avant : {current}")

        created = 0
        for v in targets:
            montant = float(v.montant_total or 0)
            if montant <= 0:
                continue

            # create Paiement
            p = Paiement(montant=montant, mode_paiement=v.mode_paiement or 'espèce', date_paiement=datetime.utcnow(), vente_id=v.id)
            db.session.add(p)
            db.session.flush()  # get p.id

            # create MouvementCaisse
            solde_avant = current
            solde_apres = solde_avant + montant
            m = MouvementCaisse(type='encaisse', montant=montant, reference=f'backfill-vente-{v.id}', date=datetime.utcnow(), paiement_id=p.id, vente_id=v.id, utilisateur='system-backfill', solde_avant=solde_avant, solde_apres=solde_apres, notes='Backfill automatique')
            db.session.add(m)

            # update running solde
            current = solde_apres
            created += 1

        # persist new solde
        ParametreSysteme.set_value('solde_caisse', current, type_valeur='number')
        db.session.commit()

        print(f"Backfill appliqué : {created} paiements + mouvements créés")
        print(f"Solde caisse après : {current}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Appliquer les changements en base')
    args = parser.parse_args()

    app = create_app()
    if args.apply:
        targets, total = preview(app)
        if not targets:
            print('Aucune vente à backfiller.')
            return
        print('\n--- Confirmation requise ---')
        print(f"Vous vous apprêtez à créer {len(targets)} paiements pour un total de {total} (backup recommandé).\n")
        ans = input('Confirmer et appliquer ? (oui/non): ').strip().lower()
        if ans in ('oui', 'o', 'yes', 'y'):
            apply_backfill(app, targets)
        else:
            print('Abandon.')
    else:
        preview(app)


if __name__ == '__main__':
    main()
