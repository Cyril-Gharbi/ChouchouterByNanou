import hashlib
import secrets
from datetime import datetime, timezone

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Admin, User, UserRequest
from app.utils import send_email, verifier_email


def init_routes(app):
    account_bp = Blueprint("account", __name__)

    # User registration (GET shows form, POST processes registration)
    @account_bp.route("/register", methods=["GET", "POST"], endpoint="register")
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]

            try:
                verifier_email(email)
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("account.register"))

            if "consent_privacy" not in request.form:
                flash(
                    "Vous devez accepter la politique de confidentialité "
                    "pour créer un compte.",
                    "error",
                )
                return redirect(url_for("account.register"))

            if len(password) < 8:
                flash("Le mot de passe doit comporter au moins 8 caractères.", "error")
                return redirect(url_for("account.register"))

            admin_email = current_app.config.get("MAIL_DEFAULT_SENDER")

            # Vérifier si un utilisateur actif existe déjà avec cet email
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Un compte avec cet email existe déjà.", "error")
                return redirect(url_for("account.register"))

            # Vérifier si le username est déjà pris par un utilisateur actif
            if User.query.filter(User.username == username).first():
                flash("Nom d'utilisateur déjà utilisé", "error")
                return redirect(url_for("account.register"))

            # Vérifier si une demande existe déjà avec ce mail
            if UserRequest.query.filter_by(email=email).first():
                flash("Une demande avec cet email est déjà en attente.", "error")
                return redirect(url_for("main.accueil"))

            # ✅ Nouvelle demande
            try:
                new_request = UserRequest(username=username, email=email)
                new_request.set_password(password)
                db.session.add(new_request)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Une erreur est survenue : email ou pseudo déjà utilisé", "error")
                return redirect(url_for("account.register"))

            flash(
                "Votre demande de création de compte a bien été prise en compte."
                "\n\nUne validation va être effectuée.",
                "info",
            )
            send_email(
                subject="Nouvelle demande d'inscription",
                recipients=[admin_email],
                body=(
                    f"Nouvelle demande de compte pour : {username}, {email}."
                    "\n\nValidez-la depuis l'interface admin."
                ),
            )
            send_email(
                subject="Votre demande d'inscription",
                recipients=[email],
                body=(
                    f"Bonjour {username},"
                    "\n\nMerci beaucoup pour votre demande d'inscription."
                    "\n\nVotre requête sera traitée dans les plus brefs délais."
                    "\n\nÀ très bientôt,\nL'équipe Chouchouter"
                ),
            )
            return redirect(url_for("main.accueil"))

        return render_template("account_user/register.html")

    # User login route (GET shows form, POST processes login)
    @account_bp.route("/login", methods=["GET", "POST"], endpoint="login")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("main.connection"))

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

                    next_page = request.form.get("next") or request.args.get("next")
                    return redirect(next_page or url_for("main.connection"))
                else:
                    flash("Mot de passe incorrect", "error")
                    return render_template(
                        "account_user/connection.html", error="Mot de passe incorrect"
                    )

            # Admin login check
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                login_user(admin)
                flash("Bienvenue dans le dashboard d'administration", "admin_success")
                return redirect(url_for("admin.admin_dashboard"))

            # Invalid credentials
            flash("Identifiants incorrects", "admin_danger")
            return render_template(
                "account_user/connection.html", error="Identifiants incorrects"
            )

        next_page = request.args.get("next")
        return render_template("account_user/connection.html", next=next_page)

    # Logout user by clearing session
    @account_bp.route("/logout", endpoint="logout")
    def logout():
        logout_user()
        return redirect(url_for("main.accueil"))

    # Delete user account (GET shows form, POST processes deletion)
    @account_bp.route(
        "/delete_account", methods=["GET", "POST"], endpoint="delete_account"
    )
    def delete_account():
        if not current_user.is_authenticated:
            return redirect(url_for("main.accueil"))

        if request.method == "POST":
            password = request.form["password"]

            if current_user.check_password(password):
                user = current_user
                user_email = current_user.email
                user_username = current_user.username

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
                logout_user()

                send_email(
                    subject="Nous sommes tristes de vous voir partir 💔",
                    recipients=[user_email],
                    body=(
                        f"Bonjour {user_username},\n\n"
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
                flash("Votre compte a été supprimé et anonymisé.", "success")
                return redirect(url_for("main.accueil"))
            else:
                flash("Mot de passe incorrect", "admin_error")
                return render_template(
                    "account_user/delete_account.html", error="Mot de passe incorrect"
                )

        return render_template("account_user/delete_account.html")

    return account_bp
