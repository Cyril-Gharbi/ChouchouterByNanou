import os
from functools import wraps

from bson import ObjectId
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pymongo.database import Database
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Admin, Comment, User
from app.utils import (
    generate_password_reset_token,
    send_email,
    verify_password_reset_token,
)


def init_routes(app, mongo_db: Database):
    admin_bp = Blueprint("admin", __name__)

    # Decorator to require admin login for protected routes
    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "admin_id" not in session:
                flash("Vous devez être connecté en tant qu'administrateur.")
                return redirect(url_for("admin.admin_login"))
            return f(*args, **kwargs)

        return decorated

    # Admin login route
    @admin_bp.route("/admin/login", methods=["GET", "POST"], endpoint="admin_login")
    def admin_login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session["admin_id"] = admin.id
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return render_template(
                    "account_user/connection.html", error="Identifiants invalides"
                )
        return render_template("account_user/connection.html")

    # Admin dashboard showing all users
    @admin_bp.route(
        "/admin/dashboard", methods=["GET", "POST"], endpoint="admin_dashboard"
    )
    @admin_required
    def admin_dashboard():
        if mongo_db is None:
            return "MongoDB non configuré"
        mdb = mongo_db
        prestations = list(mdb.Prestations.find())
        users = User.query.filter_by(is_approved=True, deleted_at=None).all()

        # Folder containing the images - absolute path
        folder = current_app.config["UPLOAD_FOLDER"]

        if request.method == "POST" and "photo" in request.files:
            photo = request.files["photo"]
            if photo.filename == "":
                flash("Aucun fichier sélectionné.", "error")
                return redirect(url_for("admin.admin_dashboard"))

            if not allowed_file(photo.filename):
                flash("Extension de fichier non autorisée.", "error")
                return redirect(url_for("admin.admin_dashboard"))

            # Securing the file name
            filename = secure_filename(str(photo.filename))
            save_path = os.path.join(folder, filename)

            # save
            photo.save(save_path)
            flash("Photo ajoutée avec succès.", "success")
            return redirect(url_for("admin.admin_dashboard"))

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
                    return redirect(url_for("admin.admin_dashboard"))
            except (ValueError, TypeError):
                flash("Ordre invalide. Veuillez entrer un entier.", "error")
                return redirect(url_for("admin.admin_dashboard"))

            new_prestation = {
                "category": category,
                "name": name,
                "description": description,
                "price": price,
                "order": order,
            }

            mdb.Prestations.update_many(
                {"order": {"$gte": order}}, {"$inc": {"order": 1}}
            )
            mdb.Prestations.insert_one(new_prestation)
            flash("Prestation ajoutée.", "success")
            return redirect(url_for("admin.admin_dashboard"))

        category_order = ["Semi-permanent", "Extension", "Nail art"]

        prestations = list(mdb.Prestations.find({}))
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
    @admin_bp.route(
        "/admin/user/edit/<int:user_id>",
        methods=["GET", "POST"],
        endpoint="admin_edit_user",
    )
    @admin_required
    def admin_edit_user(user_id):
        user = User.query.get_or_404(user_id)
        if request.method == "POST":
            user.username = request.form["username"]
            user.firstname = request.form["firstname"]
            user.lastname = request.form["lastname"]
            fidelity_str = request.form.get("fidelity_level")
            try:
                user.fidelity_level = int(fidelity_str) if fidelity_str else 0
            except ValueError:
                user.fidelity_level = 0
            user.email = request.form["email"]
            db.session.commit()
            flash("Utilisateur modifié.")
            return redirect(url_for("admin.admin_dashboard"))
        return render_template("admin/admin_edit_user.html", user=user)

    # Admin logout route
    @admin_bp.route("/admin/logout", endpoint="admin_logout")
    @admin_required
    def admin_logout():
        session.pop("admin_id", None)
        return redirect(url_for("admin.admin_login"))

    # Admin deletes a user by user ID
    @admin_bp.route(
        "/admin/user/delete/<int:user_id>",
        methods=["POST"],
        endpoint="admin_delete_user",
    )
    @admin_required
    def admin_delete_user(user_id):
        admin = Admin.query.get(session.get("admin_id"))
        if not admin:
            flash("Admin introuvable ou non connecté.", "error")
            return redirect(url_for("admin.admin_dashboard"))
        success = admin.delete_user(user_id)
        if success:
            flash("Utilisateur supprimé.")
        else:
            flash("Utilisateur introuvable.")
        return redirect(url_for("admin.admin_dashboard"))

    # Photo upload and delete for admin
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    @admin_bp.route(
        "/admin/delete_photo/<filename>",
        methods=["POST"],
        endpoint="admin_delete_photo",
    )
    @admin_required
    def admin_delete_photo(filename):
        image_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(image_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"L'image {filename} a été supprimée.")
        else:
            flash("Image introuvable.")
        return redirect(url_for("admin.admin_dashboard") + "#renvoi-photos")

    # Request password reset: send email with reset token
    @admin_bp.route(
        "/admin/reset_password", methods=["GET", "POST"], endpoint="admin_reset_request"
    )
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
                    return redirect(url_for("admin.admin_reset_request"))

            token = generate_password_reset_token(email, user_type)
            reset_url = url_for("admin.admin_reset_token", token=token, _external=True)

            subject = "Réinitialisation de votre mot de passe"
            text_body = (
                f"Pour réinitialiser votre mot de passe, cliquez ici : {reset_url}"
            )
            html_body = f"""
            <p>Pour réinitialiser votre mot de passe, cliquez ici :</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            """

            ok = send_email(
                subject=subject, recipients=[email], body=text_body, html=html_body
            )

            if ok:
                flash("Un email de réinitialisation a été envoyé à votre adresse.")
            else:
                flash(
                    "Votre demande est enregistrée, mais l'email n'a pas pu être envoyé"
                    " pour le moment."
                )

            return redirect(url_for("account.login"))

        # GET : afficher le formulaire
        return render_template("account_user/reset_password_request.html")

    @admin_bp.route(
        "/admin/reset_password/<token>",
        methods=["GET", "POST"],
        endpoint="admin_reset_token",
    )
    def admin_reset_token(token):
        email, user_type = verify_password_reset_token(token)

        if not email or user_type != "admin":
            flash("Le lien est invalide ou a expiré.", "danger")
            return redirect(url_for("admin.admin_reset_request"))

        admin = Admin.query.filter_by(email=email).first_or_404()

        if request.method == "POST":
            password = request.form.get("password")
            admin.set_password(password)
            db.session.commit()
            flash("Votre mot de passe a été réinitialisé.", "success")
            return redirect(url_for("account.login"))

        return render_template("admin/admin_reset_token.html")

    # Edit rates
    @admin_bp.route(
        "/admin/rate/edit/<id>", methods=["GET", "POST"], endpoint="edit_rate"
    )
    @admin_required
    def edit_rate(id):
        mdb = mongo_db
        # Retrieve the existing service
        prestation = mdb.Prestations.find_one({"_id": ObjectId(id)})
        if not prestation:
            flash("Prestation introuvable.", "error")
            return redirect(url_for("admin.admin_dashboard"))

        if request.method == "POST":
            # Retrieve the form data
            category = request.form.get("category")
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")
            order_str = request.form.get("order")
            new_order = int(order_str) if order_str is not None else 1

            if not category or not name or not description or not price:
                flash("Tous les champs sont obligatoires.", "error")
                return redirect(url_for("admin.edit_rate", id=id))

            old_order = prestation.get("order")

            if new_order != old_order:
                if new_order < old_order:
                    mdb.Prestations.update_many(
                        {"order": {"$gte": new_order, "$lt": old_order}},
                        {"$inc": {"order": 1}},
                    )
                else:
                    mdb.Prestations.update_many(
                        {"order": {"$gt": old_order, "$lte": new_order}},
                        {"$inc": {"order": -1}},
                    )

            # Update the service in base
            mdb.Prestations.update_one(
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
            return redirect(url_for("admin.admin_dashboard") + "#renvoi-prestations")

        # GET: display the form with the existing data
        return render_template(
            "admin/admin_edit_prestation.html", prestation=prestation
        )

    # Delete rates
    @admin_bp.route(
        "/admin/delete/<id>", methods=["POST"], endpoint="delete_prestation"
    )
    @admin_required
    def delete_prestation(id):
        mdb = mongo_db
        prestation = mdb.Prestations.find_one({"_id": ObjectId(id)})
        if prestation and "order" in prestation:
            deleted_order = int(prestation["order"] or 0)
            mdb.Prestations.delete_one({"_id": ObjectId(id)})
            mdb.Prestations.update_many(
                {"order": {"$gt": deleted_order}}, {"$inc": {"order": -1}}
            )
            flash("Prestation supprimée.", "success")
        else:
            flash("Prestation introuvable ou ordre manquant.", "error")
        return redirect(url_for("admin.admin_dashboard") + "#renvoi-prestations")

    @admin_bp.route("/admin/pending_users", endpoint="pending_users")
    @admin_required
    def pending_users():
        users = User.query.filter_by(is_approved=False).all()
        return render_template("admin/admin_approbation.html", users=users)

    @admin_bp.route(
        "/admin/process_user_request/<int:user_id>",
        methods=["POST"],
        endpoint="process_user_request",
    )
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

        return redirect(url_for("admin.pending_users"))

    @admin_bp.route(
        "/admin/comment/toggle/<int:comment_id>",
        methods=["POST"],
        endpoint="admin_toggle_comment",
    )
    @admin_required
    def admin_toggle_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        comment.is_visible = not comment.is_visible
        db.session.commit()
        flash("Statut du commentaire modifié.", "success")
        return redirect(url_for("admin.admin_dashboard") + "#renvoi-commentaires")

    @admin_bp.route(
        "/admin/comment/delete/<int:comment_id>",
        methods=["POST"],
        endpoint="admin_delete_comment",
    )
    @admin_required
    def admin_delete_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash("Commentaire supprimé.", "info")
        return redirect(url_for("admin.admin_dashboard") + "#renvoi-commentaires")

    return admin_bp
