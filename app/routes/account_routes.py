from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from ..models import User, Admin


# User registration (GET shows form, POST processes registration)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        
        if User.query.filter_by(username=username).first():
            return "Nom d'utilisateur déjà utilisé"
        
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, fidelity_level=0, fidelity_cycle=0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Log user in after registration
        session["user"] = {
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "fidelity_level": user.fidelity_level,
            "fidelity_cycle": user.fidelity_cycle
        }
        return redirect(url_for("connection"))
    return render_template("register.html")

# User login route (GET shows form, POST processes login)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Save user info in session
            session["user"] = {
                "username": user.username,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "fidelity_level": user.fidelity_level,
                "fidelity_cycle": user.fidelity_cycle
            }
            next_page = request.form.get("next")
            return redirect(next_page or url_for("connection"))

        # Admin login check
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))

        # Invalid credentials
        return render_template("connection.html", error="Identifiants incorrects")

    next_page = request.args.get("next")
    return render_template("connection.html", next=next_page)

# Logout user by clearing session
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("accueil"))

# Delete user account (GET shows form, POST processes deletion)
@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user" not in session:
        return redirect(url_for("accueil"))
    
    if request.method == "POST":
        username = session["user"]["username"]
        password = request.form["password"]
        user_to_delete = User.query.filter_by(username=username).first()
    
        if user_to_delete and user_to_delete.check_password(password):
            db.session.delete(user_to_delete)
            db.session.commit()
            session.pop("user", None)
            return redirect(url_for("accueil"))
        else:
            return render_template("delete_account.html", error="Mot de passe incorrect")
    
    return render_template("delete_account.html")