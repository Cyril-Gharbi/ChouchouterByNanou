import tempfile

import pytest
from mongomock import MongoClient

from app import create_app
from app import db as _db


class _FakeMongo:
    """Wrapper Mongo factice basé sur mongomock."""

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client["chouchouter"]

    def __getattr__(self, name):
        return getattr(self.db, name)


@pytest.fixture(scope="session")
def app():
    """Application Flask configurée pour les tests fonctionnels."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "secret-test",
            "UPLOAD_FOLDER": tempfile.mkdtemp(),
        }
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Fixture DB SQLAlchemy (rollback après chaque test)."""
    yield _db
    _db.session.rollback()


@pytest.fixture(scope="session")
def mongo_db():
    """Fixture Mongo factice pour tests fonctionnels."""
    fake_mongo = _FakeMongo()
    return fake_mongo.db


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def client_mongo(app, mongo_db):
    """Client Flask avec Mongo dispo."""
    return app.test_client()


@pytest.fixture(autouse=True)
def no_mail(monkeypatch):
    """Empêche l'envoi réel d'e-mails pendant les tests."""
    monkeypatch.setattr("app.utils.send_email", lambda *a, **k: None)
