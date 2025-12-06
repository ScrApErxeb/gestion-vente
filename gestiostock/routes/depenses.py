from flask import request, redirect, url_for, flash, render_template, jsonify, Blueprint
from models import db, Depense, ParametreSysteme, MouvementCaisse
from flask_login import current_user, login_required
from datetime import datetime

depenses_bp = Blueprint('depenses', __name__, url_prefix='/depenses')


@depenses_bp.route("", methods=["GET"])
@login_required
def depenses():
    liste = Depense.query.order_by(Depense.date.desc()).all()
    solde = ParametreSysteme.get_value("solde_caisse", 0)
    return render_template("depenses.html", depenses=liste, solde=solde)


@depenses_bp.route("/add", methods=["POST"])
@login_required
def depenses_add():
    # Support both form POST and AJAX
    data = request.form if request.form else request.get_json(silent=True) or {}
    libelle = data.get("libelle")
    montant_raw = data.get("montant")
    description = data.get("description", "")

    if not libelle or not montant_raw:
        msg = "Veuillez fournir un libellé et un montant valides."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': msg}), 400
        flash(msg, "danger")
        return redirect(url_for("depenses.depenses"))

    try:
        montant = float(montant_raw)
    except Exception:
        msg = "Montant invalide."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': msg}), 400
        flash(msg, "danger")
        return redirect(url_for("depenses.depenses"))

    solde = float(ParametreSysteme.get_value("solde_caisse", 0) or 0)

    # Vérification fonds disponibles
    if montant > solde:
        msg = "Fonds insuffisants pour effectuer cette dépense."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': msg}), 400
        flash(f"❌ {msg}", "danger")
        return redirect(url_for("depenses.depenses"))

    try:
        # Ajouter dépense
        dep = Depense(libelle=libelle, montant=montant, description=description)
        db.session.add(dep)
        db.session.flush()

        # Mise à jour caisse
        nouveau_solde = solde - montant
        ParametreSysteme.set_value("solde_caisse", nouveau_solde, type_valeur="number")

        # Historiser mouvement caisse
        utilisateur = getattr(current_user, 'username', None) if current_user and hasattr(current_user, 'username') else None
        mouvement = MouvementCaisse(
            type='decaisse',
            montant=montant,
            vente_id=None,
            paiement_id=None,
            utilisateur=utilisateur,
            solde_avant=solde,
            solde_apres=nouveau_solde,
            notes=f'Dépense: {libelle}',
            date=datetime.utcnow()
        )
        db.session.add(mouvement)

        db.session.commit()

        # Response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'ok',
                'depense': {
                    'id': dep.id,
                    'libelle': dep.libelle,
                    'montant': dep.montant,
                    'description': dep.description,
                    'date': dep.date.isoformat()
                },
                'nouveau_solde': nouveau_solde
            })

        flash("✅ Dépense enregistrée et caisse mise à jour.", "success")
        return redirect(url_for("depenses.depenses"))
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur depenses_add: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
        flash(f"Erreur lors de l'enregistrement de la dépense: {e}", "danger")
        return redirect(url_for("depenses.depenses"))
