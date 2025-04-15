from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def accueil():
    return render_template("accueil.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/tarifs")
def tarifs():
    return render_template("tarifs.html")

if __name__ == "__main__":
    app.run(debug=True)