from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


from models import db, create_app, User, Comment
from datetime import datetime

import logging
from logging import FileHandler



load_dotenv()

app = create_app()
migrate = Migrate(app, db)


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
        return redirect(url_for("login"))  # Redirige vers la page de login si l'utilisateur n'est pas connecté
    
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





# connexion utilisateurs...
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
                "fidelity_level": user.fidelity_level
            }

            next_page = request.form.get("next")
            return redirect(next_page or url_for("connection"))
        else:
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
        
        if User.query.filter_by(username=username).first():
            return "Nom d'utilisateur déjà utilisé"
        
        user = User(username=username, firstname=firstname, lastname=lastname, fidelity_level=0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user"] = {
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "fidelity_level": user.fidelity_level
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
            db.session.delete(user_to_delete)  # Supprime l'utilisateur de la base de données
            db.session.commit()  # Applique la suppression  
            session.pop("user", None)  # Déconnecte l'utilisateur en supprimant sa session
            return redirect(url_for("accueil"))  # Redirige vers la page d'accueil après suppression
        else:
            return render_template("delete_account.html", error="Mot de passe incorrect")
    
    return render_template("delete_account.html")


    # Fidélité QRCode

@app.route("/scan")
def scan():
    if "user" not in session:
        # Redirige vers login avec next paramètre
        return redirect(url_for("login", next=url_for("scan")))

    username = session["user"]["username"]
    user = User.query.filter_by(username=username).first()

    if user:
        # Incrémente fidélité
        if user.fidelity_level < 10:
            user.fidelity_level += 1
        else:
            user.fidelity_level = 1

        db.session.commit()
        fresh_user = User.query.filter_by(username=username).first()

        # Remplace toute la session utilisateur pour forcer la mise à jour
        session["user"] = {
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "fidelity_level": user.fidelity_level
        }

    return redirect(url_for("connection", scan_success="1"))

        
if __name__ == "__main__":
    app.run(debug=True)