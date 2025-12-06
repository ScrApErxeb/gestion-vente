from flask import request, redirect, url_for, flash
from app import app, db
from models import Paiement, ParametreSysteme, MouvementCaisse
from flask_login import current_user


@app.route("/paiement/add", methods=["POST"])
def paiement_add():
    vente_id = request.form.get("vente_id")
    try:
        montant = float(request.form.get("montant") or 0)
    except (TypeError, ValueError):
        flash("Montant invalide.", "danger")
        return redirect(url_for("ventes"))

    try:
        # Enregistrement paiement
        p = Paiement(vente_id=vente_id, montant=montant)
        db.session.add(p)
        db.session.flush()  # obtenir p.id avant commit

        # Créditer la caisse automatiquement
        solde_avant = ParametreSysteme.get_value("solde_caisse", 0)
        solde_apres = solde_avant + montant
        ParametreSysteme.set_value("solde_caisse", solde_apres, type_valeur="number")

        # Historiser le mouvement de caisse
        utilisateur = getattr(current_user, 'username', None) if current_user and hasattr(current_user, 'username') else None
        mouvement = MouvementCaisse(
            type='encaisse',
            montant=montant,
            paiement_id=p.id,
            vente_id=vente_id,
            utilisateur=utilisateur,
            solde_avant=solde_avant,
            solde_apres=solde_apres,
            notes='Paiement enregistré via formulaire'
        )
        db.session.add(mouvement)

        db.session.commit()

        flash("💰 Paiement enregistré. Caisse mise à jour.", "success")
        return redirect(url_for("ventes_detail", id=vente_id))

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur paiement_add: {e}")
        flash(f"Erreur lors de l'enregistrement du paiement: {e}", "danger")
        return redirect(url_for("ventes"))
