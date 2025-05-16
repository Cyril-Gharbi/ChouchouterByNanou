from flask import render_template, request, redirect, url_for, session, flash
from . import app, db, mongo_db
from .models import User, Comment, Admin, FidelityRewardLog
from datetime import datetime
import os

@app.route("/")
def accueil():
    return render_template("accueil.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/rates")
def rates():
    return render_template("rates.html")

@app.route("/cgu")
def cgu():
    return render_template("cgu.html")

@app.route("/mentions")
def mentions():
    return render_template("mentions.html")

@app.route("/connection")
def connection():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    return render_template("connection.html", user=user)

@app.route('/comments')
def comments():
    all_comments = Comment.query.order_by(Comment.date.desc()).all()
    return render_template('comments.html', comments=all_comments)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session:
        flash("Vous devez être connecté pour laisser un commentaire.")
        return redirect(url_for('connection'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash("Le commentaire ne peut pas être vide.")
        return redirect(url_for('comments'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("Utilisateur non trouvé.")
        return redirect(url_for('connection'))

    comment = Comment(content=content, user=user)
    db.session.add(comment)
    db.session.commit()

    flash("Merci pour votre commentaire !")
    return redirect(url_for('comments'))

@app.route("/tablettes")
def afficher_tablettes():
    tablettes = list(mongo_db.tablettes.find())
    return render_template("tablettes.html", tablettes=tablettes)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
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

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))

        return render_template("connection.html", error="Identifiants incorrects")

    next_page = request.args.get("next")
    return render_template("connection.html", next=next_page)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("accueil"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        
        if User.query.filter_by(username=username).first():
            return "Nom d'utilisateur déjà utilisé"
        
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, fidelity_level=0, fidelity_cycle=0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user"] = {
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "fidelity_level": user.fidelity_level,
            "fidelity_cycle": user.fidelity_cycle
        }
        return redirect(url_for("connection"))
    return render_template("register.html")

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
            return redirect(url_for("accueil"))
        else:
            return render_template("delete_account.html", error="Mot de passe incorrect")
    
    return render_template("delete_account.html")

# QR CODE

@app.route("/scan")
def scan():
    if "user" not in session:
        return redirect(url_for("login", next=url_for("scan")))

    username = session["user"]["username"]
    user = User.query.filter_by(username=username).first()

    if user:
        if user.fidelity_level < 10:
            user.fidelity_level += 1
        else:
            user.fidelity_level = 1
            user.fidelity_cycle += 1

        db.session.commit()
        update_user_session(user)


        # Palier fidélité récompensé ?
        if user.fidelity_level in [4, 9]:
            # Vérifie si mail déjà envoyé pour ce palier
            existing_reward = FidelityRewardLog.query.filter_by(
                user_id=user.id, 
                level_reached=user.fidelity_level,
                cycle_number=user.fidelity_cycle
            ).first()

            if not existing_reward:
                # Envoi du mail
                send_discount_email(user, user.fidelity_level)
                print(f"Envoi du mail pour user {user.email} au niveau {user.fidelity_level}")
                # Enregistrement du mail envoyé pour ce palier
                new_reward = FidelityRewardLog(
                    user_id=user.id,
                    level_reached=user.fidelity_level,
                    cycle_number=user.fidelity_cycle
                )
                db.session.add(new_reward)
                db.session.commit()

    return redirect(url_for("connection", scan_success="1"))

# ADMIN ROUTES

from functools import wraps
from flask import flash

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Identifiants invalides")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template("admin_dashboard.html", users=users)

@app.route("/admin/user/delete/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    admin = Admin.query.get(session["admin_id"])
    success = admin.delete_user(user_id)
    if success:
        flash("Utilisateur supprimé.")
    else:
        flash("Utilisateur introuvable.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/user/edit/<int:user_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.firstname = request.form["firstname"]
        user.lastname = request.form["lastname"]
        user.fidelity_level = int(request.form["fidelity_level"])
        user.email = request.form["email"]
        db.session.commit()
        flash("Utilisateur modifié.")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit_user.html", user=user)



# GENERATE PASSWORD MAILS

from flask_mail import Message
from . import mail
from .utils import generate_password_reset_token, verify_password_reset_token, send_discount_email, update_user_session

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_password_reset_token(user.email)
            reset_url = url_for('reset_token', token=token, _external=True)
            msg = Message("Réinitialisation de votre mot de passe",
                          sender=os.getenv('MAIL_USERNAME'),
                          recipients=[email])
            msg.body = f"Pour réinitialiser votre mot de passe, cliquez ici: {reset_url}"
            mail.send(msg)
            flash("Un email de réinitialisation a été envoyé à votre adresse.")
            return redirect(url_for('login'))
        else:
            flash("Aucun compte associé à cet email.")
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    email = verify_password_reset_token(token)
    if not email:
        flash("Le lien de réinitialisation est invalide ou a expiré.")
        return redirect(url_for('reset_request'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Utilisateur non trouvé.")
        return redirect(url_for('reset_request'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user.set_password(new_password)
        db.session.commit()
        flash("Votre mot de passe a été mis à jour.")
        return redirect(url_for('login'))

    return render_template('reset_password_form.html')