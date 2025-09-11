import hashlib
import secrets
from datetime import datetime, timezone

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Admin, User
from app.utils import send_email, verifier_email


def init_routes(app):
    # User registration (GET shows form, POST processes registration)
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            firstname = request.form["firstname"]
            lastname = request.form["lastname"]
            email = request.form["email"]

            try:
                verifier_email(email)
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("register"))

            if "consent_privacy" not in request.form:
                flash(
                    "Vous devez accepter la politique de confidentialité "
                    "pour créer un compte.",
                    "error",
                )
                return redirect(url_for("register"))

            if len(password) < 8:
                flash("Le mot de passe doit comporter au moins 8 caractères.", "error")

            user = User.query.filter_by(email=email).first()

            if user:
                if user.deleted_at is not None:
                    username_taken = User.query.filter(
                        User.username == username,
                        User.deleted_at.is_(None),
                        User.id != user.id,
                    ).first()
                    if username_taken:
                        flash(
                            "Le nom d'utilisateur est déjà utilisé "
                            "par un autre compte actif",
                            "error",
                        )
                        return redirect(url_for("register"))

                    user.username = username
                    user.firstname = firstname
                    user.lastname = lastname
                    user.set_password(password)
                    user.deleted_at = None
                    user.consent_privacy = True
                    user.consent_date = datetime.now(timezone.utc)
                    user.is_approved = False
                    try:
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        flash("Une erreur est survenue : doublon détecté.", "error")
                        return redirect(url_for("register"))

                    flash(
                        "Votre compte a été réactivé avec succès. "
                        "Une validation sera effectuée.",
                        "info",
                    )
                    send_email(
                        subject="Nouvelle demande d'inscription",
                        recipients=[current_app.config.get("MAIL_USERNAME")],
                        body=(
                            "Nouvelle demande de réactivation de compte pour : "
                            f"{firstname} {lastname} ({email}).\n\n"
                            "Validez-la depuis l'interface admin."
                        ),
                    )
                    send_email(
                        subject="Votre demande d'inscription",
                        recipients=[user.email],
                        body=(
                            f"Bonjour {user.firstname},\n\n"
                            "Merci beaucoup pour votre demande de réinscription.\n\n"
                            "Votre requête sera traitée dans les plus brefs délais.\n\n"
                            "À très bientôt,\nL'équipe Chouchouter"
                        ),
                    )
                    return redirect(url_for("accueil"))
                else:
                    flash("Un compte avec cet email existe déjà.", "error")

            if User.query.filter_by(username=username, deleted_at=None).first():
                flash("Nom d'utilisateur déjà utilisé", "error")
                return redirect(url_for("register"))

            utc_now = datetime.now(timezone.utc)

            user = User(
                username=username,
                firstname=firstname,
                lastname=lastname,
                email=email,
                fidelity_level=0,
                fidelity_cycle=0,
                consent_privacy=True,
                consent_date=utc_now,
                is_approved=False,
            )
            user.set_password(password)
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Une erreur est survenue : email ou pseudo déjà utilisé", "error")
                return redirect(url_for("register"))

            flash(
                "Votre demande de création de compte a bien été prise en compte.\n\n"
                "Une validation va être effectuée.",
                "info",
            )
            send_email(
                subject="Nouvelle demande d'inscription",
                recipients=[current_app.config.get("MAIL_DEFAULT_SENDER")],
                body=(
                    "Nouvelle demande de compte pour : "
                    f"{firstname} {lastname}, {email}.\n\n"
                    "Validez-la depuis l'interface admin."
                ),
            )
            send_email(
                subject="Votre demande d'inscription",
                recipients=[user.email],
                body=(
                    f"Bonjour {user.firstname},\n\n"
                    "Merci beaucoup pour votre demande d'inscription.\n\n"
                    "Votre requête sera traitée dans les plus brefs délais.\n\n"
                    "À très bientôt,\nL'équipe Chouchouter"
                ),
            )
            return redirect(url_for("register"))
        return render_template("account_user/register.html")

    # User login route (GET shows form, POST processes login)
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("connection"))

        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if user:
                if not user.is_approved:
                    flash(
                        "Votre compte n'a pas encore été approuvé. Veuillez patienter.",
                        "warning",
                    )
                    return render_template(
                        "account_user/connection.html", error="Compte non approuvé"
                    )

                if user.check_password(password):
                    login_user(user)

                    next_page = request.form.get("next")
                    return redirect(next_page or url_for("connection"))
                else:
                    flash("Mot de passe incorrect", "error")
                    return render_template(
                        "account_user/connection.html", error="Mot de passe incorrect"
                    )

            # Admin login check
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session["admin_id"] = admin.id
                return redirect(url_for("admin_dashboard"))

            # Invalid credentials
            flash("Identifiants incorrects")
            return render_template(
                "account_user/connection.html", error="Identifiants incorrects"
            )

        next_page = request.args.get("next")
        return render_template("account_user/connection.html", next=next_page)

    # Logout user by clearing session
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("accueil"))

    # Delete user account (GET shows form, POST processes deletion)
    @app.route("/delete_account", methods=["GET", "POST"])
    def delete_account():
        if not current_user.is_authenticated:
            return redirect(url_for("accueil"))

        if request.method == "POST":
            password = request.form["password"]

            if current_user.check_password(password):
                user = current_user
                user_email = current_user.email
                user_firstname = current_user.firstname

                for comment in user.comments:
                    comment.user_id = None

                anonym_suffix = hashlib.sha256(
                    str(datetime.now(timezone.utc)).encode()
                ).hexdigest()[:6]
                user.username = f"deleted_user_{user.id}_{anonym_suffix}"
                user.email = (
                    f"deleted_user_{user.id}_{secrets.token_hex(4)}@example.com"
                )
                user.deleted_at = datetime.now(timezone.utc)
                user.is_anonymized = True

                db.session.commit()
                db.session.flush()
                logout_user()

                send_email(
                    subject="Nous sommes tristes de vous voir partir 💔",
                    recipients=[user_email],
                    body=(
                        f"Bonjour {user_firstname},\n\n"
                        "Nous avons bien pris en compte la suppression "
                        "de votre compte.\n\n"
                        "C’est toujours un petit pincement au cœur de voir partir l’un"
                        " de nos clients. Sachez que votre présence au sein de "
                        "Chouchouter a été appréciée, et nous espérons que vous avez "
                        "passé de bons moments à nos côtés.\n\n"
                        "Si un jour l’envie vous prend de revenir, ce sera avec un "
                        "immense plaisir que nous vous accueillerons de nouveau.\n\n"
                        "En attendant, nous vous souhaitons le meilleur pour la suite."
                        "\nPrenez soin de vous.\n\n"
                        "Avec toute notre bienveillance,\nL’équipe Chouchouter"
                    ),
                )

                return redirect(url_for("accueil"))
            else:
                flash("Mot de passe incorrect")
                return render_template(
                    "account_user/delete_account.html", error="Mot de passe incorrect"
                )

        return render_template("account_user/delete_account.html")
