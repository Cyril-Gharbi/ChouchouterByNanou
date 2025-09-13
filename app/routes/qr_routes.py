from flask import Blueprint, redirect, url_for
from flask_login import current_user, login_user

from app.extensions import db
from app.models import FidelityRewardLog, User
from app.utils import send_discount_email  # la fonction est bien dans app/utils.py


def init_routes(app):
    qr_bp = Blueprint("qr", __name__)

    @qr_bp.route("/scan", endpoint="scan")
    def scan():
        # 1) Si pas connecté -> redirige vers /login avec next=/scan
        if not current_user.is_authenticated:
            return redirect(url_for("account.login", next=url_for("qr.scan")))

        # 2) Récupère l'utilisateur via Flask-Login
        user = User.query.filter_by(id=current_user.id).first()
        if not user:
            return redirect(url_for("main.connection"))

        # 3) Sécurise les None
        if user.fidelity_level is None:
            user.fidelity_level = 0
        if user.fidelity_cycle is None:
            user.fidelity_cycle = 0

        # 4) Incrémente fidélité (1..10), puis reset à 1 et +1 cycle
        if user.fidelity_level < 10:
            user.fidelity_level += 1
        else:
            user.fidelity_level = 1
            user.fidelity_cycle += 1

        db.session.commit()

        # 5) Rafraîchit current_user pour que le template voie la nouvelle valeur
        login_user(user)

        # 6) Récompense aux paliers (ex: 4 et 9)
        if user.fidelity_level in [5, 10]:
            existing = FidelityRewardLog.query.filter_by(
                user_id=user.id,
                level_reached=user.fidelity_level,
                cycle_number=user.fidelity_cycle,
            ).first()

            if not existing:
                try:
                    send_discount_email(user, user.fidelity_level)
                finally:
                    # on log la récompense même si l’email échoue
                    new_reward = FidelityRewardLog(
                        user_id=user.id,
                        level_reached=user.fidelity_level,
                        cycle_number=user.fidelity_cycle,
                    )
                    db.session.add(new_reward)
                    db.session.commit()

        # 7) Retour sur la page "connexion" (ton écran d’accueil protégé)
        return redirect(url_for("main.connection", scan_success="1"))

    return qr_bp
