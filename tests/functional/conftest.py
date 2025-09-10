import tempfile

import pytest

from app import create_app
from app import db as _db
from app.extensions import init_mongo, mail
from app.routes import (
    account_routes,
    admin_routes,
    comment_routes,
    main_routes,
    qr_routes,
    reset_password_routes,
)


@pytest.fixture(scope="session")
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "secret",
            "UPLOAD_FOLDER": tempfile.mkdtemp(),
        }
    )

    # init extensions
    mail.init_app(app)
    mongo_db = init_mongo()

    # register routes
    main_routes.init_routes(app, mongo_db)
    account_routes.init_routes(app)
    admin_routes.init_routes(app, mongo_db)
    comment_routes.init_routes(app)
    qr_routes.init_routes(app)
    reset_password_routes.init_routes(app)

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture(autouse=True)
def no_mail(monkeypatch):
    """Empêche Flask-Mail d'envoyer de vrais mails pendant les tests"""
    monkeypatch.setattr("app.utils.mail.send", lambda msg: None)
