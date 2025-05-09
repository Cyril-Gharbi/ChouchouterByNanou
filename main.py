from flask_migrate import Migrate

from flask import Flask, render_template, request, redirect, url_for, session
from models import db, create_app, User
from dotenv import load_dotenv
import os


load_dotenv()
app = create_app()
migrate = Migrate(app, db)


@app.route("/")
def accueil():
    return render_template("accueil.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/tarifs")
def tarifs():
    return render_template("tarifs.html")

@app.route("/cgu")
def cgu():
    return render_template("cgu.html")

@app.route("/mentions")
def mentions():
    return render_template("mentions.html")

@app.route("/connexion")
def connexion():
    return render_template("connexion.html")



# connexion utilisateurs...
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = User.query.filter_by(username=username).first()
        if users and users.check_password(password):
            session["user"] = {
                "username": users.username,
                "firstname": users.firstname,
                "lastname": users.lastname,
            }
            return redirect(url_for("connexion"))
        else:
            return render_template("connexion.html", error="Identifiants incorrects")
    
    return render_template("connexion.html")

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
        
        users = User(username=username, firstname=firstname, lastname=lastname)
        users.set_password(password)
        db.session.add(users)
        db.session.commit()

        session["users"] = {
            "username": users.username,
            "firstname": users.firstname,
            "lastname": users.lastname
        }
        return redirect(url_for("connexion"))
    return render_template("register.html")

@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "users" not in session:
        return redirect(url_for("accueil"))
    
    username = session["users"]["username"]
    user_to_delete = User.query.filter_by(username=username).first()
    
    if user_to_delete:
        db.session.delete(user_to_delete)  # Supprime l'utilisateur de la base de données
        db.session.commit()  # Applique la suppression
        
        session.pop("users", None)  # Déconnecte l'utilisateur en supprimant sa session
        return redirect(url_for("accueil"))  # Redirige vers la page d'accueil après suppression
    
    return "Erreur, utilisateur introuvable", 404

        
if __name__ == "__main__":
    app.run(debug=True)