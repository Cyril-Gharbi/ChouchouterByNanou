# flake8: noqa: E402
import inspect
import os
from datetime import datetime, timezone
from typing import Any

import pytz
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_login import current_user
from flask_mail import Message
from flask_wtf.csrf import generate_csrf

from app.models import Admin, User

load_dotenv()

from .extensions import csrf, db, init_mongo, login_manager, mail


# --- Fallback Mongo ---
class _FakeCollection:
    def find(self, *a, **k):
        return []

    def insert_one(self, *a, **k):
        class R:
            inserted_id = "0"

        return R()

    def delete_one(self, *a, **k):
        class R:
            deleted_count = 0

        return R()

    def update_one(self, *a, **k):
        class R:
            modified_count = 0

        return R()


class _FakeMongo:
    Prestations = _FakeCollection()


def _called_from_unit_tests() -> bool:
    """Si create_app() est invoqué depuis tests/unit/*, on laisse les tests enregistrer les routes eux-mêmes."""
    for frame in inspect.stack():
        fn = frame.filename.replace("\\", "/")
        if "/tests/unit/" in fn:
            return True
    return False


def create_app(config: dict | None = None):
    app = Flask(__name__)

    # default configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "images", "realisations"
    )

    # Flask-Mail
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.mail.me.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = (
        os.getenv("MAIL_DEFAULT_SENDER") or app.config["MAIL_USERNAME"]
    )

    # Apply specific configuration (tests, dev)
    if config:
        app.config.update(config)

    # Initialization of extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = (  # pyright: ignore[reportAttributeAccessIssue]
        "account.login"
    )
    csrf.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None

        # sécurité : s'assurer qu'on manipule une string
        user_id = str(user_id)

        if user_id.startswith("user-"):
            return User.query.get(int(user_id.split("-", 1)[1]))
        elif user_id.startswith("admin-"):
            return Admin.query.get(int(user_id.split("-", 1)[1]))

        # fallback : ancien cookie sans préfixe
        return None

    @app.context_processor
    def inject_user_logged_in():
        return dict(
            user_logged_in=current_user.is_authenticated, csrf_token=generate_csrf
        )

    # expose datetime dans Jinja
    app.jinja_env.globals.update(datetime=datetime)

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

    # --- Mongo ---
    mongo_db: Any = app.config.get("MONGO_DB")
    if mongo_db is None:
        try:
            if os.getenv("MONGO_URI"):
                mongo_db = init_mongo()
            else:
                mongo_db = _FakeMongo()
        except Exception:
            mongo_db = _FakeMongo()

    # --- Blueprints ---
    if not _called_from_unit_tests():
        from .routes import (
            account_routes,
            admin_routes,
            comment_routes,
            main_routes,
            qr_routes,
            reset_password_routes,
        )

        app.register_blueprint(main_routes.init_routes(app, mongo_db))
        app.register_blueprint(account_routes.init_routes(app))
        app.register_blueprint(admin_routes.init_routes(app, mongo_db))
        app.register_blueprint(comment_routes.init_routes(app))
        app.register_blueprint(qr_routes.init_routes(app))
        app.register_blueprint(reset_password_routes.init_routes(app))

    return app
