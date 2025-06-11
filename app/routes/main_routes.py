from flask import render_template, request, redirect, url_for, session, current_app
from app import app, mongo_db, db
from bson import ObjectId
import os



# Home page route
@app.route("/")
def accueil():
    return render_template("accueil.html")

# Portfolio page route
@app.route('/portfolio')
def portfolio():
    image_folder = 'images/realisations'  # dossier dans /static/
    full_path = os.path.join(current_app.root_path, 'static', image_folder)
    try:
        files = os.listdir(full_path)
    except FileNotFoundError:
        files = []
    valid_images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Trier les fichiers par date de modification décroissante
    valid_images.sort(key=lambda x: os.path.getmtime(os.path.join(full_path, x)), reverse=True)

    # Générer les chemins relatifs
    images = [f"{image_folder}/{f}" for f in valid_images]
    return render_template('portfolio.html', images=images)

# Rates page route
@app.route("/rates")
def rates():
    prestations = list(mongo_db.Prestations.find())
    for p in prestations:
        p['_id'] = str(p['_id'])

    return render_template("rates.html", prestations=prestations)

# Display tablets collection from MongoDB (NoSQL)
@app.route("/tablettes")
def afficher_tablettes():
    tablettes = list(mongo_db.tablettes.find())
    return render_template("tablettes.html", tablettes=tablettes)

# User connection page, requires user to be logged in
@app.route("/connection")
def connection():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    return render_template("connection.html", user=user)


# Terms and conditions page route
@app.route("/cgu")
def cgu():
    return render_template("cgu.html")

# Legal mentions page route
@app.route("/mentions")
def mentions():
    return render_template("mentions.html")

@app.route("/politique")
def politique():
    return render_template("politique_confidentialite.html")


@app.route("/contact")
def contact():
    return render_template("contact_us.html")