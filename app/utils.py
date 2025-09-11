import logging
import os

import requests  # type: ignore
from flask import current_app, session
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from app.extensions import mail
from app.models import User


def verifier_email(email):
    """Checks that the email contains a '@'."""
    if "@" not in email:
        raise ValueError("Email invalide")


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

    subject = "🎉 Félicitations pour votre fidélité !"
    text_body = (
        f"Bonjour {user.firstname},\n\n"
        f"Bravo ! Vous avez atteint le niveau {level} de fidélité.\n"
        f"Vous bénéficiez de {discount}% de réduction sur votre prochaine séance !\n\n"
        "À très bientôt ✨\n"
        "L'équipe Chouchouter"
    )
    html_body = f"""
    <p>Bonjour {user.firstname},</p>
    <p>Bravo ! Vous avez atteint le niveau {level} de fidélité.</p>
    <p><strong>{discount}%</strong> de réduction sur votre prochaine séance 🎁</p>
    <p>À très bientôt ✨<br>L'équipe Chouchouter</p>
    """

    ok = send_email(
        subject=subject, recipients=[user.email], body=text_body, html=html_body
    )

    return ok


def send_email(subject, recipients, body, html=None):
    """
    Envoie un email en fonction du provider choisi :
    - SMTP (iCloud, Gmail, etc.)
    - SendGrid (API HTTP, recommandé en hébergeur cloud)
    """

    provider = os.getenv("MAIL_PROVIDER", "smtp")

    if provider == "smtp":
        try:
            msg = Message(subject=subject, recipients=recipients, body=body, html=html)
            mail.send(msg)
            logging.info(f"Email envoyé via SMTP à {recipients}")
            return True
        except Exception as e:
            logging.error(f"Erreur SMTP: {e}")
            return False

    elif provider == "sendgrid":
        try:
            api_key = os.getenv("SENDGRID_API_KEY")
            sender = os.getenv("MAIL_DEFAULT_SENDER")

            if not api_key or not sender:
                logging.error("Config SendGrid manquante (API key ou sender).")
                return False

            data = {
                "personalizations": [{"to": [{"email": r} for r in recipients]}],
                "from": {"email": sender},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": body},
                    {"type": "text/html", "value": html or body},
                ],
            }

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=data,
                timeout=10,
            )

            if response.status_code == 202:
                logging.info(f"Email envoyé via SendGrid à {recipients}")
                return True
            else:
                logging.error(
                    f"Erreur SendGrid: {response.status_code}, {response.text}"
                )
                return False

        except Exception as e:
            logging.error(f"Erreur lors de l'envoi via SendGrid: {e}")
            return False


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
