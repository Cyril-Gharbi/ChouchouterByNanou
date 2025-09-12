from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Admin, User
from app.utils import (
    generate_password_reset_token,
    send_email,
    verify_password_reset_token,
)


def init_routes(app):
    reset_password_bp = Blueprint("reset_password", __name__)

    @reset_password_bp.route(
        "/reset_user_password", methods=["GET", "POST"], endpoint="reset_user_password"
    )
    def reset_user_password():
        token = request.args.get("token")
        if not token:
            abort(403)

        if request.method == "GET":
            return render_template("account_user/reset_password_form.html", token=token)

        new_password = request.form.get("new_password")

        if not new_password or len(new_password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.")
            return redirect(
                url_for("reset_password.reset_user_password") + f"?token={token}"
            )

        email, user_type = verify_password_reset_token(token)

        if email is None:
            flash("Lien invalide ou expiré", "error")
            return redirect(url_for("reset_password.reset_password_request"))

        if user_type == "admin":
            user = Admin.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()

        if not user:
            flash("Utilisateur introuvable.")
            return redirect(url_for("reset_password.reset_user_request"))

        user.set_password(new_password)
        db.session.commit()

        flash("Votre mot de passe a été mis à jour.")
        return redirect(url_for("account.login"))

    @reset_password_bp.route(
        "/reset_user_request", methods=["GET", "POST"], endpoint="reset_user_request"
    )
    def reset_user_request():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()

            if not user or not email:
                flash("Aucun compte utilisateur associé à cet email.")
                return redirect(url_for("reset_password.reset_user_request"))

            token = generate_password_reset_token(email, "user")
            reset_url = url_for(
                "reset_password.reset_user_password", token=token, _external=True
            )

            subject = "Réinitialisation de votre mot de passe"
            text_body = (
                f"Pour réinitialiser votre mot de passe, cliquez ici : {reset_url}"
            )
            html_body = f"""
            <p>Pour réinitialiser votre mot de passe, cliquez ici :</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            """

            ok = send_email(
                subject=subject, recipients=[email], body=text_body, html=html_body
            )

            if ok:
                flash("Un email de réinitialisation a été envoyé à votre adresse.")
            else:
                flash(
                    "Votre demande est enregistrée, mais l'email n'a pas pu être "
                    "envoyé pour le moment."
                )

            return redirect(url_for("account.login"))

        return render_template("account_user/reset_password_request.html")

    return reset_password_bp
