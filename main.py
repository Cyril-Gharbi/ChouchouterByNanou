from flask import Flask, render_template, request, redirect, url_for, session
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

home_dir = os.getenv('HOME')  # Récupère la variable d'environnement HOME
print(f"Le répertoire HOME est : {home_dir}")



from models import db, create_app, User

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
    if "user" not in session:
        return redirect(url_for("login"))  # Redirige vers la page de login si l'utilisateur n'est pas connecté
    
    user = session["user"]
    return render_template("connexion.html", user=user)





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
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            else:
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
        return redirect(url_for("connexion"))
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

        # Met à jour la session
        session["user"]["fidelity_level"] = user.fidelity_level

    return redirect(url_for("connexion", scan_success="1"))

        
if __name__ == "__main__":
    app.run(debug=True)