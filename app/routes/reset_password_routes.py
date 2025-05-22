from flask import request, render_template, redirect, url_for, abort, flash, current_app
from ..models import User, Admin
from ..utils import verify_password_reset_token
from app import app, db


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")
    if not token:
        abort(403)

    if request.method == "GET":
        return render_template("reset_password.html", token=token)

    new_password = request.form.get("new_password")
    result = verify_password_reset_token(token, current_app.config["SECRET_KEY"])
    if not result:
        flash("Lien invalide ou expiré.")
        return redirect(url_for('reset_request'))

    email, user_type = result

    if user_type == "admin":
        user = Admin.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(email=email).first()

    if not user:
        flash("Utilisateur introuvable.")
        return redirect(url_for('reset_request'))

    user.set_password(new_password)
    db.session.commit()

    flash("Votre mot de passe a été mis à jour.")
    return redirect(url_for("login"))
