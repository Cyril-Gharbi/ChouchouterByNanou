from flask import Blueprint, redirect, url_for
from flask_login import current_user

from app.extensions import db
from app.models import FidelityRewardLog, User
from app.utils import send_discount_email


def init_routes(app):
    qr_bp = Blueprint("qr", __name__)

    @qr_bp.route("/scan", endpoint="scan")
    def scan():
        # If not connected -> redirects to /login with next=/scan
        if not current_user.is_authenticated:
            return redirect(url_for("account.login", next=url_for("qr.scan")))

        # Retrieves the user via Flask-Login
        user = User.query.filter_by(id=current_user.id).first()
        if not user:
            return redirect(url_for("main.connection"))

        # Retrieves the user’s last loyalty log
        last_log = (
            FidelityRewardLog.query.filter_by(user_id=user.id)
            .order_by(FidelityRewardLog.date.desc())
            .first()
        )

        if not last_log:
            fidelity_level = 1
            fidelity_cycle = 0
        else:
            fidelity_level = last_log.fidelity_level
            fidelity_cycle = last_log.fidelity_cycle

            if fidelity_level < 10:
                fidelity_level += 1
            else:
                fidelity_level = 1
                fidelity_cycle += 1

                # Reward at the levels (ex: 4 et 9)
            if fidelity_level in [4, 9]:
                try:
                    send_discount_email(user, fidelity_level)
                finally:
                    # we already log the reward via new_log, so nothing to add here
                    pass

        # new log
        new_log = FidelityRewardLog(
            user_id=user.id,
            fidelity_level=fidelity_level,
            fidelity_cycle=fidelity_cycle,
            level_reached=fidelity_level,
            cycle_number=fidelity_cycle,
        )
        db.session.add(new_log)
        db.session.commit()

        # Back to the "login" page (your protected home screen)
        return redirect(url_for("main.connection", scan_success="1"))

    return qr_bp
