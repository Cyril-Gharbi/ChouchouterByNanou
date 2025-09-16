from sqlalchemy import func
from sqlalchemy.orm import aliased

from app import db
from app.models import FidelityRewardLog, User


def get_users_with_last_log():
    # Sous-requête : date max par user
    subq = (
        db.session.query(
            FidelityRewardLog.user_id,
            func.max(FidelityRewardLog.date).label("max_date"),
        )
        .group_by(FidelityRewardLog.user_id)
        .subquery()
    )

    last_log = aliased(FidelityRewardLog)

    # Requête principale
    results = (
        db.session.query(
            User.id,
            User.username,
            User.email,
            User.consent_date,
            last_log.fidelity_level,
            last_log.fidelity_cycle,
        )
        .outerjoin(subq, subq.c.user_id == User.id)
        .outerjoin(
            last_log,
            (last_log.user_id == subq.c.user_id) & (last_log.date == subq.c.max_date),
        )
        .filter(User.is_approved.is_(True), User.deleted_at.is_(None))
        .all()
    )

    # Transformer en dictionnaires pour le template
    users = [
        {
            "id": r[0],
            "username": r[1],
            "email": r[2],
            "consent_date": r[3],
            "fidelity_level": r[4] if r[4] is not None else 0,
            "fidelity_cycle": r[5] if r[5] is not None else 0,
        }
        for r in results
    ]

    return users
