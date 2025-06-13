from flask import render_template, request, redirect, url_for, session, flash, current_app
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app import app, db
from ..models import User, Admin
from ..utils import is_existing_user, send_email
import textwrap


# User registration (GET shows form, POST processes registration)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]

        if "consent_privacy" not in request.form:
            flash("Vous devez accepter la politique de confidentialité pour créer un compte.", "error")
            return redirect(url_for("register"))
        
        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur déjà utilisé", "error")
            return redirect(url_for("register"))
        
        if User.query.filter_by(email=email).first():
            flash("Un compte avec cet email existe déjà.", "error")
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
            is_approved=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Votre demande de création de compte a bien été prise en compte. Une validation va être effectuée.", "info")

        send_email(
            subject="Nouvelle demande d'inscription",
            recipients=[current_app.config.get("MAIL_USERNAME")],
            body=f"Nouvelle demande de compte pour : {firstname} {lastname} ({email}). \n\nValidez-la depuis l'interface admin."
        )

        send_email(
            subject="Votre demande d'inscription",
            recipients=[user.email],
            body=textwrap.dedent(f"""\
            Bonjour {user.firstname},
            
            Merci beaucoup pour votre demande d'inscription.
            
            Votre requête sera traitée dans les plus brefs délais.
            
            À très bientôt,
            L'équipe Chouchouter""")
        )

        return redirect(url_for("register"))
    return render_template("register.html")


# User login route (GET shows form, POST processes login)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user:
            if not user.is_approved:
                flash("Votre compte n'a pas encore été approuvé. Veuillez patienter.", "warning")
                return render_template("connection.html", error="Compte non approuvé")


            if user and user.check_password(password):
                # Save user info in session
                session["user"] = {
                    "username": user.username,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "email": user.email,
                    "fidelity_level": user.fidelity_level,
                    "fidelity_cycle": user.fidelity_cycle
                }
                next_page = request.form.get("next")
                return redirect(next_page or url_for("connection"))
            else:
                flash("Mot de passe incorrect.", "error")
                return render_template("connection.html", error="Mot de passe incorrect")

        # Admin login check
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))

        # Invalid credentials
        flash("Identifiants incorrects")
        return render_template("connection.html", error="Identifiants incorrects")

    next_page = request.args.get("next")
    return render_template("connection.html", next=next_page)



# Logout user by clearing session
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("accueil"))



# Delete user account (GET shows form, POST processes deletion)
@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user" not in session:
        return redirect(url_for("accueil"))
    
    if request.method == "POST":
        username = session["user"]["username"]
        password = request.form["password"]
        user_to_delete = User.query.filter_by(username=username).first()
    
        if user_to_delete and user_to_delete.check_password(password):
            db.session.delete(user_to_delete)
            db.session.commit()
            session.pop("user", None)

            send_email(
                subject="Nous sommes tristes de vous voir partir 💔",
                recipients=[user_to_delete.email],
                body=textwrap.dedent(f"""\
                Bonjour {user_to_delete.firstname},
                
                Nous avons bien pris en compte la suppression de votre compte.

                C’est toujours un petit pincement au cœur de voir partir l’un de nos clients. Sachez que votre présence au sein de Chouchouter a été appréciée, et nous espérons que vous avez passé de bons moments à nos côtés.

                Si un jour l’envie vous prend de revenir, ce sera avec un immense plaisir que nous vous accueillerons de nouveau.

                En attendant, nous vous souhaitons le meilleur pour la suite.
                Prenez soin de vous.

                Avec toute notre bienveillance,
                L’équipe Chouchouter""")
            )

            return redirect(url_for("accueil"))
        else:
            flash("Mot de passe incorrect")
            return render_template("delete_account.html", error="Mot de passe incorrect")
    
    return render_template("delete_account.html")