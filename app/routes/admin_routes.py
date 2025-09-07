import os
from functools import wraps

from bson import ObjectId
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Message
from werkzeug.utils import secure_filename

from app.extensions import db, mail
from app.models import Admin, Comment, User
from app.utils import (
    generate_password_reset_token,
    send_email,
    verify_password_reset_token,
)


def init_routes(app, mongo_db=None):
    # Decorator to require admin login for protected routes
    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "admin_id" not in session:
                flash("Vous devez être connecté en tant qu'administrateur.")
                return redirect(url_for("admin_login"))
            return f(*args, **kwargs)

        return decorated

    # Admin login route
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
                return render_template(
                    "account_user/connection.html", error="Identifiants invalides"
                )
        return render_template("account_user/connection.html")

    # Admin dashboard showing all users
    @app.route("/admin/dashboard", methods=["GET", "POST"])
    @admin_required
    def admin_dashboard():
        if mongo_db is None:
            return "MongoDB non configuré"
        mdb = mongo_db
        prestations = list(mdb.Prestations.find())
        users = User.query.filter_by(is_approved=True, deleted_at=None).all()

        # Dossier contenant les images — chemin absolu
        folder = os.path.join(current_app.root_path, UPLOAD_FOLDER)

        if request.method == "POST" and "photo" in request.files:
            photo = request.files["photo"]
            if photo.filename == "":
                flash("Aucun fichier sélectionné.", "error")
                return redirect(url_for("admin_dashboard"))

            if not allowed_file(photo.filename):
                flash("Extension de fichier non autorisée.", "error")
                return redirect(url_for("admin_dashboard"))

            # Sécurisation du nom de fichier
            filename = secure_filename(photo.filename)
            save_path = os.path.join(folder, filename)

            # Sauvegarde
            photo.save(save_path)
            flash("Photo ajoutée avec succès.", "success")
            return redirect(url_for("admin_dashboard"))

        images = [f for f in sorted(os.listdir(folder)) if allowed_file(f)]

        if "category" in request.form:
            category = request.form.get("category")
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")
            order_str = request.form.get("order")

            try:
                order = int(order_str) if order_str is not None else 1
                if order < 1:
                    flash("L'ordre doit être un entier positif.", "error")
                    return redirect(url_for("admin_dashboard"))
            except (ValueError, TypeError):
                flash("Ordre invalide. Veuillez entrer un entier.", "error")
                return redirect(url_for("admin_dashboard"))

            new_prestation = {
                "category": category,
                "name": name,
                "description": description,
                "price": price,
                "order": order,
            }

            db.Prestations.update_many(
                {"order": {"$gte": order}}, {"$inc": {"order": 1}}
            )
            db.Prestations.insert_one(new_prestation)
            flash("Prestation ajoutée.", "success")
            return redirect(url_for("admin_dashboard"))

        category_order = ["Semi-permanent", "Extension", "Nail art"]

        prestations = list(mongo_db.Prestations.find({}))
        prestations.sort(
            key=lambda p: (
                (
                    category_order.index(p["category"])
                    if p["category"] in category_order
                    else len(category_order)
                ),
                p.get("order", 999),
            )
        )
        for p in prestations:
            if "order" not in p:
                p["order"] = 9999
            p["_id"] = str(p["_id"])

        comments = Comment.query.order_by(Comment.date.desc()).limit(50).all()
        return render_template(
            "admin/admin_dashboard.html",
            users=users,
            images=images,
            prestations=prestations,
            comments=comments,
        )

    # Admin edits user details (GET shows form, POST updates data)
    @app.route("/admin/user/edit/<int:user_id>", methods=["GET", "POST"])
    @admin_required
    def admin_edit_user(user_id):
        user = User.query.get_or_404(user_id)
        if request.method == "POST":
            user.firstname = request.form["firstname"]
            user.lastname = request.form["lastname"]
            fidelity_str = request.form.get("fidelity_level")
            user.fidelity_level = (
                int(request.form["fidelity_str"]) if fidelity_str is not None else 0
            )
            user.email = request.form["email"]
            db.session.commit()
            flash("Utilisateur modifié.")
            return redirect(url_for("admin_dashboard"))
        return render_template("admin/admin_edit_user.html", user=user)

    # Admin logout route
    @app.route("/admin/logout")
    @admin_required
    def admin_logout():
        session.pop("admin_id", None)
        return redirect(url_for("admin_login"))

    # Admin deletes a user by user ID
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

    # Photo upload and delete for admin
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    UPLOAD_FOLDER = "static/images/realisations"  # adapte si besoin

    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    @app.route("/admin/delete_photo/<filename>", methods=["POST"])
    @admin_required
    def admin_delete_photo(filename):
        image_folder = os.path.join(
            current_app.root_path, "static", "images", "realisations"
        )
        file_path = os.path.join(image_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"L'image {filename} a été supprimée.")
        else:
            flash("Image introuvable.")
        return redirect(url_for("admin_dashboard") + "#renvoi-photos")

    # Request password reset: send email with reset token
    @app.route("/admin/reset_password", methods=["GET", "POST"])
    def admin_reset_request():
        if request.method == "POST":
            email = request.form.get("email")
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                user_type = "admin"
                email = admin.email
            else:
                user = User.query.filter_by(email=email).first()
                if user:
                    user_type = "user"
                    email = user.email
                else:
                    flash("Aucun compte associé à cet email.")
                    return redirect(url_for("admin_reset_request"))

            token = generate_password_reset_token(email, user_type)
            reset_url = url_for("admin_reset_token", token=token, _external=True)
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

        # GET : on affiche juste le formulaire, pas de flash d'erreur
        return render_template("account_user/reset_password_request.html")

    @app.route("/admin/reset_token/<token>", methods=["GET", "POST"])
    def admin_reset_token(token):
        result = verify_password_reset_token(token, current_app.config["SECRET_KEY"])
        if not result:
            flash("Le lien de réinitialisation est invalide ou a expiré.")
            return redirect(url_for("admin_reset_request"))

        email, user_type = result

        if user_type == "admin":
            user = Admin.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()

        if not user:
            flash("Utilisateur non trouvé.")
            return redirect(url_for("admin_reset_request"))

        if request.method == "POST":
            new_password = request.form.get("password")
            if not new_password:
                flash("Le mot de passe ne peut pas être vide.")
                return redirect(url_for("admin_reset_token", token=token))

            user.set_password(new_password)
            db.session.commit()
            flash("Votre mot de passe a été mis à jour.")
            return redirect(url_for("login"))

        return render_template("account_user/reset_password_form.html")

    # Edit rates
    @app.route("/admin/rate/edit/<id>", methods=["GET", "POST"])
    @admin_required
    def edit_rate(id):
        db = mongo_db
        # Récupérer la prestation existante
        prestation = db.Prestations.find_one({"_id": ObjectId(id)})
        if not prestation:
            flash("Prestation introuvable.", "error")
            return redirect(url_for("admin_dashboard"))

        if request.method == "POST":
            # Récupérer les données du formulaire
            category = request.form.get("category")
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")
            order_str = request.form.get("order")
            new_order = int(order_str) if order_str is not None else 1

            if not category or not name or not description or not price:
                flash("Tous les champs sont obligatoires.", "error")
                return redirect(url_for("edit_rate", id=id))

            old_order = prestation.get("order")

            if new_order != old_order:
                if new_order < old_order:
                    db.Prestations.update_many(
                        {"order": {"$gte": new_order, "$lt": old_order}},
                        {"$inc": {"order": 1}},
                    )
                else:
                    db.Prestations.update_many(
                        {"order": {"$gt": old_order, "$lte": new_order}},
                        {"$inc": {"order": -1}},
                    )

            # Mettre à jour la prestation en base
            db.Prestations.update_one(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "category": category,
                        "name": name,
                        "description": description,
                        "price": price,
                        "order": new_order,
                    }
                },
            )
            flash("Prestation mise à jour avec succès.", "success")
            return redirect(url_for("admin_dashboard") + "#renvoi-prestations")

        # GET: afficher le formulaire avec les données existantes
        return render_template(
            "admin/admin_edit_prestation.html", prestation=prestation
        )

    # Delete rates
    @app.route("/admin/delete/<id>", methods=["POST"])
    @admin_required
    def delete_prestation(id):
        db = mongo_db
        prestation = db.Prestations.find_one({"_id": ObjectId(id)})
        if prestation and "order" in prestation:
            deleted_order = int(prestation["order"] or 0)
            db.Prestations.delete_one({"_id": ObjectId(id)})
            db.Prestations.update_many(
                {"order": {"$gt": deleted_order}}, {"$inc": {"order": -1}}
            )
            flash("Prestation supprimée.", "success")
        else:
            flash("Prestation introuvable ou ordre manquant.", "error")
        return redirect(url_for("admin_dashboard") + "#renvoi-prestations")

    @app.route("/admin/pending_users")
    @admin_required
    def pending_users():
        users = User.query.filter_by(is_approved=False).all()
        return render_template("admin/admin_approbation.html", users=users)

    @app.route("/admin/process_user_request/<int:user_id>", methods=["POST"])
    @admin_required
    def process_user_request(user_id):
        user = User.query.get_or_404(user_id)
        action = request.form.get("action")

        if action == "approve":
            user.is_approved = True
            db.session.commit()
            send_email(
                subject="Acceptation de votre demande de création de compte",
                recipients=[user.email],
                body=(
                    f"Félicitations {user.firstname} !\n\n"
                    "Votre demande de création de compte a été acceptée. "
                    "Nous sommes ravis de vous compter parmi nos clients.\n\n"
                    "Vous pouvez dès à présent vous connecter "
                    "à votre espace personnel.\n\n"
                    "À très bientôt,\nL'équipe Chouchouter"
                ),
            )
            flash(f"Utilisateur {user.username} validé avec succès.", "success")

        elif action == "refuse":
            db.session.delete(user)
            db.session.commit()
            send_email(
                subject="Refus de votre demande de création de compte",
                recipients=[user.email],
                body=(
                    f"Bonjour {user.firstname},\n\n"
                    "Nous vous remercions pour votre intérêt.\n\n"
                    "Malheureusement, nous ne pouvons donner suite à "
                    "votre demande de création de compte.\n\n"
                    "Celui-ci est réservé exclusivement à notre clientèle, dans le "
                    "cadre du suivi personnalisé, du programme de fidélité, et de la "
                    "possibilité de partager un retour d'expérience sur "
                    "nos prestations.\n\n"
                    "Nous serions ravis de vous compter prochainement "
                    "parmi nos clients fidèles.\n\n"
                    "À très bientôt,\nL'équipe Chouchouter"
                ),
            )
            flash(f"Utilisateur {user.username} supprimé.", "info")

        return redirect(url_for("pending_users"))

    @app.route("/admin/comment/toggle/<int:comment_id>", methods=["POST"])
    @admin_required
    def admin_toggle_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        comment.is_visible = not comment.is_visible
        db.session.commit()
        flash("Statut du commentaire modifié.", "success")
        return redirect(url_for("admin_dashboard") + "#renvoi-commentaires")

    @app.route("/admin/comment/delete/<int:comment_id>", methods=["POST"])
    @admin_required
    def admin_delete_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash("Commentaire supprimé.", "info")
        return redirect(url_for("admin_dashboard") + "#renvoi-commentaires")
