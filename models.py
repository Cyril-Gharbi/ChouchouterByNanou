from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os


load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    print("DATABASE_URL =", repr(os.getenv("DATABASE_URL")))
    db.init_app(app)
    return app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    fidelity_level = db.Column(db.Integer, default=0)

    def set_password(self, password):
        """Hash the password before storing it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Lien avec l'utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))