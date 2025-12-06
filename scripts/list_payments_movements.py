from __future__ import print_function
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
PKG = os.path.join(ROOT, 'gestiostock')
if PKG not in sys.path: sys.path.insert(0, PKG)

from gestiostock.app import create_app
try:
    from models import db, Paiement, MouvementCaisse, Vente
except ImportError:
    from gestiostock.models import db, Paiement, MouvementCaisse, Vente
from sqlalchemy import asc

app = create_app()
with app.app_context():
    print('PAIEMENTS (id, vente_id, montant, mode, date, utilisateur, reference)')
    for p in db.session.query(Paiement).order_by(asc(Paiement.id)).all():
        print('id={} vente_id={} montant={:,.2f} mode={} date={} user={} ref={}'.format(p.id, p.vente_id, float(p.montant or 0), getattr(p, 'mode_paiement', None), getattr(p, 'date_paiement', None), getattr(p, 'utilisateur', None), getattr(p, 'reference', None)))
    print('\nMOUVEMENTS CAISSE (id, type, montant, vente_id, paiement_id, utilisateur, reference, date, solde_avant, solde_apres)')
    for m in db.session.query(MouvementCaisse).order_by(asc(MouvementCaisse.id)).all():
        print('id={} type={} montant={:,.2f} vente_id={} paiement_id={} user={} ref={} date={} solde_avant={} solde_apres={}'.format(m.id, m.type, float(m.montant or 0), m.vente_id, m.paiement_id, m.utilisateur, m.reference, m.date, m.solde_avant, m.solde_apres))
    print('\nVENTES (id, montant_total, statut_paiement, mode_paiement, date)')
    for v in db.session.query(Vente).order_by(asc(Vente.id)).all():
        print('id={} montant={:,.2f} statut={} mode={} date={}'.format(v.id, float(v.montant_total or 0), v.statut_paiement, v.mode_paiement, v.date_vente))
