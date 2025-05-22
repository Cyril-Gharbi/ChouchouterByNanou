from flask import render_template, request, redirect, url_for, session, current_app, flash
from app import app, db, mail
from ..models import User, Admin
from functools import wraps
from werkzeug.utils import secure_filename
from ..utils import generate_password_reset_token, verify_password_reset_token, send_discount_email, update_user_session
from flask_mail import Message
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
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template("admin_dashboard.html", users=users)

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




# Gallery for admin to view photos
@app.route("/galerie")
@admin_required
def galerie():
    # Dossier contenant les images
    folder = os.path.join(app.static_folder, "images/realisations")

    # Extensions autorisées (modifie si besoin)
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Lister les fichiers images
    images = [
        os.path.join("images/realisations", f)
        for f in sorted(os.listdir(folder))
        if os.path.splitext(f)[1].lower() in allowed_extensions
    ]

    return render_template("galerie.html", images=images)


# Photo upload and delete for admin
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'app/static/images/realisations'  # adapte si besoin

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/upload-photo', methods=['GET', 'POST'])
@admin_required
def admin_upload_photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            flash('Photo ajoutée avec succès !')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Format de fichier non autorisé.')
            return redirect(request.url)
    return render_template('admin_upload_photo.html')

@app.route("/admin/photos")
@admin_required
def admin_photos():
    image_folder = os.path.join(current_app.root_path, 'static', 'images', 'realisations')
    images = os.listdir(image_folder)
    images = [img for img in images if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template("admin_photos.html", images=images)

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
    return redirect(url_for('admin_photos'))


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
