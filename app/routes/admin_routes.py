from flask import render_template, request, redirect, url_for, session, current_app, flash
from app import app, db, mail, mongo_db
from ..models import User, Admin
from functools import wraps
from werkzeug.utils import secure_filename
from ..utils import generate_password_reset_token, verify_password_reset_token, send_discount_email, update_user_session
from flask_mail import Message
from bson import ObjectId
import os



# Decorator to require admin login for protected routes
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
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
            return render_template("admin_login.html", error="Identifiants invalides")
    return render_template("admin_login.html")






# Admin dashboard showing all users
@app.route("/admin/dashboard", methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    db = mongo_db
    users = User.query.all()
    # Dossier contenant les images — chemin absolu
    folder = os.path.join(current_app.root_path, UPLOAD_FOLDER)

    if request.method == 'POST' and 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename == '':
            flash("Aucun fichier sélectionné.", "error")
            return redirect(url_for('admin_dashboard'))

        if not allowed_file(photo.filename):
            flash("Extension de fichier non autorisée.", "error")
            return redirect(url_for('admin_dashboard'))

        # Sécurisation du nom de fichier
        filename = secure_filename(photo.filename)
        save_path = os.path.join(folder, filename)

        # Sauvegarde
        photo.save(save_path)
        flash("Photo ajoutée avec succès.", "success")
        return redirect(url_for('admin_dashboard'))
    
    images = [
        f
        for f in sorted(os.listdir(folder))
        if allowed_file(f)
    ]


    if 'category' in request.form:
        category = request.form.get("category")
        name = request.form.get("name")
        description = request.form.get("description")
        price_str = request.form.get("price")

        try:
            price = float(price_str)
            if price < 0:
                flash("Le prix ne peut pas être négatif.", "error")
                return redirect(url_for('admin_dashboard'))
        except (ValueError, TypeError):
            flash("Prix invalide. Veuillez entrer un nombre.", "error")
            return redirect(url_for('admin_dashboard'))

        new_prestation = {
            "category": category,
            "name": name,
            "description": description,
            "price": price,
        }
        db.Prestations.insert_one(new_prestation)
        flash("Prestation ajoutée.", "success")
        return redirect(url_for('admin_dashboard'))
    
    category_order = ['Semi-permanent', 'Extension', 'Nail art']
    

    prestations = list(mongo_db.Prestations.find({}))
    prestations.sort(key=lambda p: category_order.index(p['category']) if p['category'] in category_order else len(category_order))
    for p in prestations:
        p['_id'] = str(p['_id'])

    return render_template("admin_dashboard.html", users=users, images=images, prestations=prestations)







# Admin edits user details (GET shows form, POST updates data)
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

# Admin logout route
@app.route("/admin/logout")
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/images/realisations'  # adapte si besoin

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/admin/delete_photo/<filename>", methods=["POST"])
@admin_required
def admin_delete_photo(filename):
    image_folder = os.path.join(current_app.root_path, 'static', 'images', 'realisations')
    file_path = os.path.join(image_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"L'image {filename} a été supprimée.")
    else:
        flash("Image introuvable.")
    return redirect(url_for('admin_dashboard'))





# Request password reset: send email with reset token
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
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
                return redirect(url_for('reset_request'))

        token = generate_password_reset_token(email, user_type, current_app.config["SECRET_KEY"])
        reset_url = url_for('reset_token', token=token, _external=True)
        msg = Message("Réinitialisation de votre mot de passe",
                      sender=os.getenv('MAIL_USERNAME'),
                      recipients=[email])
        msg.body = f"Pour réinitialiser votre mot de passe, cliquez ici: {reset_url}"
        mail.send(msg)
        flash("Un email de réinitialisation a été envoyé à votre adresse.")
        return redirect(url_for('login'))

    # GET : on affiche juste le formulaire, pas de flash d'erreur
    return render_template('reset_password_request.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    result = verify_password_reset_token(token, current_app.config["SECRET_KEY"])
    if not result:
        flash("Le lien de réinitialisation est invalide ou a expiré.")
        return redirect(url_for('reset_request'))

    email, user_type = result

    if user_type == "admin":
        user = Admin.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(email=email).first()

    if not user:
        flash("Utilisateur non trouvé.")
        return redirect(url_for('reset_request'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        if not new_password:
            flash("Le mot de passe ne peut pas être vide.")
            return redirect(url_for('reset_token', token=token))

        user.set_password(new_password)
        db.session.commit()
        flash("Votre mot de passe a été mis à jour.")
        return redirect(url_for('login'))

    return render_template('reset_password_form.html')



# Edit rates
@app.route('/admin/rate/edit/<id>', methods=['GET', 'POST'])
@admin_required
def edit_rate(id):
    db = mongo_db
    # Récupérer la prestation existante
    prestation = db.Prestations.find_one({"_id": ObjectId(id)})
    if not prestation:
        flash("Prestation introuvable.", "error")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        # Récupérer les données du formulaire
        category = request.form.get('category')
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')

        if not category or not name or not description or not price:
            flash("Tous les champs sont obligatoires.", "error")
            return redirect(url_for('edit_rate', id=id))

        # Mettre à jour la prestation en base
        db.Prestations.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "category": category,
                "name": name,
                "description": description,
                "price": price
            }}
        )
        flash("Prestation mise à jour avec succès.", "success")
        return redirect(url_for('admin_dashboard'))

    # GET: afficher le formulaire avec les données existantes
    return render_template('admin_edit_prestation.html', prestation=prestation)



# Delete rates
@app.route("/admin/delete/<id>", methods=["POST"])
@admin_required
def delete_prestation(id):
    db = mongo_db
    db.Prestations.delete_one({"_id": ObjectId(id)})
    flash("Prestation supprimée.", "success")
    return redirect(url_for("admin_dashboard"))