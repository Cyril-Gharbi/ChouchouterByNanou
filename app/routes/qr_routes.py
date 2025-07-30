from flask import redirect, session, url_for

from app import app, db

from ..models import FidelityRewardLog, User
from ..utils import send_discount_email, update_user_session


# QR code scan route, increments user's fidelity level and handles rewards
@app.route("/scan")
def scan():
    if "user" not in session:
        return redirect(url_for("login", next=url_for("scan")))

    username = session["user"]["username"]
    user = User.query.filter_by(username=username).first()

    if user:
        # Increase fidelity level or cycle
        if user.fidelity_level < 10:
            user.fidelity_level += 1
        else:
            user.fidelity_level = 1
            user.fidelity_cycle += 1

        db.session.commit()
        update_user_session(user)

        # Check if fidelity milestone reached (level 4 or 9)
        if user.fidelity_level in [4, 9]:
            existing_reward = FidelityRewardLog.query.filter_by(
                user_id=user.id,
                level_reached=user.fidelity_level,
                cycle_number=user.fidelity_cycle,
            ).first()

            if not existing_reward:
                # Send discount email
                send_discount_email(user, user.fidelity_level)
                print(
                    f"Envoi du mail pour user {user.email} "
                    f"au niveau {user.fidelity_level}"
                )
                # Log the reward email sent
                new_reward = FidelityRewardLog(
                    user_id=user.id,
                    level_reached=user.fidelity_level,
                    cycle_number=user.fidelity_cycle,
                )
                db.session.add(new_reward)
                db.session.commit()

    return redirect(url_for("connection", scan_success="1"))
