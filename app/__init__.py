# flake8: noqa: E402
import os
from datetime import datetime, timezone

import pytz
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_login import current_user
from flask_mail import Message
from flask_wtf.csrf import generate_csrf

load_dotenv()

from .extensions import csrf, db, login_manager, mail


def create_app(config=None):
    app = Flask(__name__)

    # default configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "images", "realisations"
    )

    # Flask-Mail (will be initialized in main.py)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.mail.me.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # Apply specific configuration (tests, dev)
    if config:
        app.config.update(config)

    # Initialization of extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"  # pyright: ignore[reportAttributeAccessIssue]
    csrf.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=int(user_id), deleted_at=None).first()

    @app.context_processor
    def inject_user_logged_in():
        return dict(
            user_logged_in=current_user.is_authenticated, csrf_token=generate_csrf
        )

    # Filters for templates
    @app.template_filter("localdatetime")
    def localdatetime_filter(dt):
        if dt is None:
            return ""
        local_tz = pytz.timezone("Europe/Paris")
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        local_dt = dt.astimezone(local_tz)
        return local_dt.strftime("%d/%m/%Y à %H:%M")

    @app.template_filter("localdatetime_fr")
    def localdatetime_fr_filter(dt):
        if dt is None:
            return ""
        mois_fr = [
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ]
        local_tz = pytz.timezone("Europe/Paris")
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        local_dt = dt.astimezone(local_tz)
        return f"{local_dt.day} {mois_fr[local_dt.month-1]} {local_dt.year} à {local_dt.hour}h{local_dt.minute:02d}"

    return app
