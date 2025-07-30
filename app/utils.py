from flask import current_app, session
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from . import mail
from .models import User


# Generates a password reset token that expires after a given time (default: 1 hour)
def generate_password_reset_token(email, user_type):
    secret_key = current_app.config["SECRET_KEY"]
    s = URLSafeTimedSerializer(secret_key)
    data = {"email": email, "type": user_type}
    return s.dumps(data, salt="password-reset-salt")


# Verifies a password reset token and returns the user's email if valid
def verify_password_reset_token(token, expires_sec=3600):
    secret_key = current_app.config["SECRET_KEY"]
    s = URLSafeTimedSerializer(secret_key)
    try:
        # Try to load the email from the token; check if token has expired
        data = s.loads(token, salt="password-reset-salt", max_age=expires_sec)
        email = data.get("email")
        user_type = data.get("type")
    except Exception:
        # Return None if the token is invalid or expired
        return None, None
    return email, user_type


# Sends a loyalty discount email to the user based on their fidelity level
def send_discount_email(user, level):
    discount = 20 if level == 4 else 30
    msg = Message(
        subject="🎉 Félicitations pour votre fidélité !",
        recipients=[user.email],
        body=f"""Bonjour {user.firstname},

        Bravo ! Vous avez atteint le niveau {level} de fidélité.
        Vous bénéficiez de {discount}% de réduction sur votre prochaine séance !

        À très bientôt ✨
        L'équipe Chouchouter""",
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)


def send_email(subject, recipients, body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)


# Stores the user's information in the Flask session
def update_user_session(user):
    session["user"] = {
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "fidelity_level": user.fidelity_level,
    }


def is_existing_user(email):
    return User.query.filter_by(email=email).first() is not None
