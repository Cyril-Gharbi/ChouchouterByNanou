import os

from flask import abort, flash, redirect, render_template, request, url_for
from flask_mail import Message

from app.extensions import db, mail
from app.models import Admin, User
from app.utils import generate_password_reset_token, verify_password_reset_token


def init_routes(app):
    @app.route("/reset_user_password", methods=["GET", "POST"])
    def reset_user_password():
        token = request.args.get("token")
        if not token:
            abort(403)

        if request.method == "GET":
            return render_template("account_user/reset_password_form.html", token=token)

        new_password = request.form.get("new_password")

        if not new_password or len(new_password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.")
            return redirect(url_for("reset_user_password") + f"?token={token}")

        email, user_type = verify_password_reset_token(token)
        if not email or not user_type:
            flash("Lien invalide ou expiré.")
            return redirect(url_for("reset_user_request"))

        if user_type == "admin":
            user = Admin.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()

        if not user:
            flash("Utilisateur introuvable.")
            return redirect(url_for("reset_user_request"))

        user.set_password(new_password)
        db.session.commit()

        flash("Votre mot de passe a été mis à jour.")
        return redirect(url_for("login"))

    @app.route("/reset_user_request", methods=["GET", "POST"])
    def reset_user_request():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()
            if not user:
                flash("Aucun compte utilisateur associé à cet email.")
                return redirect(url_for("reset_user_request"))

            token = generate_password_reset_token(email, "user")
            reset_url = url_for("reset_user_password", token=token, _external=True)

            msg = Message(
                "Réinitialisation de votre mot de passe",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[email],
            )
            msg.body = (
                f"Pour réinitialiser votre mot de passe, cliquez ici: {reset_url}"
            )
            mail.send(msg)
            flash("Un email de réinitialisation a été envoyé à votre adresse.")
            return redirect(url_for("login"))

        return render_template("account_user/reset_password_request.html")
