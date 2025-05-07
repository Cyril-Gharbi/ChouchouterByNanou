from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret_super_secret"

users = {'user1': {'password': 'password123', 'firstname': 'John', 'lastname': 'Doe'}}

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
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username]['password'] == password:
            session['user'] = users[username]
            return redirect(url_for("accueil"))
        
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
        
        if username not in users:
            users[username] = {
                "password": password,
                "firstname": firstname,
                "lastname": lastname
            }
            session["user"] = {
                "username": username,
                "firstname": firstname,
                "lastname": lastname
            }
            return redirect(url_for("accueil"))
        else:
            return "Nom d'utilisateur déjà utilisé"
    return render_template("register.html")
        
if __name__ == "__main__":
    app.run(debug=True)