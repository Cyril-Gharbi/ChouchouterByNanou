import pytest

from app import create_app
from app.models import db as _db


# --- Enregistrement des routes pour les tests ---
# On fabrique un mini "mongo_db" factice qui répond à .Prestations.find()
class _FakePrestations:
    def find(self, *args, **kwargs):
        return []


class _FakeMongo:
    Prestations = _FakePrestations()


# Import des modules de routes et enregistrement sur l'app
def _register_routes(app):
    from app.routes import (
        account_routes,
        admin_routes,
        comment_routes,
        main_routes,
        qr_routes,
        reset_password_routes,
    )

    fake_mongo = _FakeMongo()
    main_routes.init_routes(app, fake_mongo)
    account_routes.init_routes(app)
    admin_routes.init_routes(app, fake_mongo)
    comment_routes.init_routes(app)
    qr_routes.init_routes(app)
    reset_password_routes.init_routes(app)


@pytest.fixture(scope="session")
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            # désactive CSRF pour simplifier les posts éventuels en test
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.app_context():
        _register_routes(app)
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db
