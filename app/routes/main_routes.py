import os

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app import app, db, mongo_db

from ..models import Comment


# Home page route
@app.route("/")
def accueil():
    return render_template("accueil.html")


# Portfolio page route
@app.route("/portfolio")
def portfolio():
    image_folder = "images/realisations"  # dossier dans /static/
    full_path = os.path.join(current_app.root_path, "static", image_folder)
    try:
        files = os.listdir(full_path)
    except FileNotFoundError:
        files = []
    valid_images = [
        f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]

    # Trier les fichiers par date de modification décroissante
    valid_images.sort(
        key=lambda x: os.path.getmtime(os.path.join(full_path, x)), reverse=True
    )

    # Générer les chemins relatifs
    images = [f"{image_folder}/{f}" for f in valid_images]
    return render_template("portfolio.html", images=images)


# Rates page route
@app.route("/rates")
def rates():
    prestations = list(mongo_db.Prestations.find())
    for p in prestations:
        p["_id"] = str(p["_id"])

    return render_template("rates.html", prestations=prestations)


# Display tablets collection from MongoDB (NoSQL)
@app.route("/tablettes")
def afficher_tablettes():
    tablettes = list(mongo_db.tablettes.find())
    return render_template("tablettes.html", tablettes=tablettes)


# Display all comments, ordered by most recent
@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        if not current_app.is_authenticated:
            flash("Vous devez être connecté pour poster un commentaire.", "warning")
            return redirect(url_for("login"))

        content = request.form.get("content", "").strip()
        if not content:
            flash("Le commentaire ne peut pas être vide.", "danger")
        else:
            new_comment = Comment(
                content=content,
                user=current_user,
                username_at_time=current_user.username,
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Commentaire publié avec succès.", "success")
        return redirect(url_for("comments"))

    comments = (
        Comment.query.filter_by(is_visible=True)
        .options(db.joinedload(Comment.user))
        .order_by(Comment.date.desc())
        .all()
    )
    return render_template("comments.html", comments=comments)


# User connection page, requires user to be logged in
@app.route("/connection")
def connection():
    return render_template("account_user/connection.html", user=current_user)


# Terms and conditions page route
@app.route("/cgu")
def cgu():
    return render_template("rgpd/cgu.html")


# Legal mentions page route
@app.route("/mentions")
def mentions():
    return render_template("rgpd/mentions.html")


@app.route("/politique")
def politique():
    return render_template("rgpd/politique_confidentialite.html")


@app.route("/contact")
def contact():
    return render_template("contact_us.html")
