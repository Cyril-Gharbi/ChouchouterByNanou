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
    # Load secret key from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # Load database connection URI from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    # Disable tracking modifications to save resources
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Flask-Mail configuration for sending emails
    app.config['MAIL_SERVER'] = 'smtp.mail.me.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    @app.context_processor
    def inject_user_logged_in():
        from flask import session
        return dict(user_logged_in=('user' in session))
    
    return app



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    fidelity_level = db.Column(db.Integer, default=0)
    fidelity_cycle = db.Column(db.Integer, default=0)
    consent_privacy = db.Column(db.Boolean, nullable=False, default=False)
    consent_date = db.Column(db.DateTime, nullable=True)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    admin = db.relationship('Admin', backref=db.backref('users', lazy=True))

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


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    email = db.Column(db.String(150), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    

class FidelityRewardLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_reached = db.Column(db.Integer, nullable=False)  # 4 ou 9
    date = db.Column(db.DateTime, default=datetime.utcnow)
    cycle_number = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='fidelity_reward_logs', passive_deletes=True)