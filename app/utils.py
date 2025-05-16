from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_password_reset_token(user_email, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_email, salt='password-reset-salt')

def verify_password_reset_token(token, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except Exception:
        return None
    return email



from flask_mail import Message
from . import mail

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
        sender=current_app.config.get("MAIL_DEFAULT_SENDER")
    )
    mail.send(msg)


from flask import session

def update_user_session(user):
    session["user"] = {
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "fidelity_level": user.fidelity_level
    }
