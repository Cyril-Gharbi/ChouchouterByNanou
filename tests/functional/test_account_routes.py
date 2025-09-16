from typing import Any

import pytest

from app import create_app
from app.models import db as _db


# Fake MongoDB pour les tests
class FakePrestations:
    def __init__(self):
        self._docs = []

    def find(self, *args, **kwargs):
        # renvoie tous les docs simulés
        return self._docs

    def insert_one(self, doc):
        self._docs.append(doc)
        return {"inserted_id": len(self._docs)}


class FakeMongo:
    def __init__(self):
        self.Prestations = FakePrestations()


# création de l'instance fake
fake_mongo: Any = FakeMongo()


@pytest.fixture()
def app_sqlite():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "secret",
        }
    )
    from app.routes import (
        account_routes,
        admin_routes,
        comment_routes,
        main_routes,
        qr_routes,
        reset_password_routes,
    )

    with app.app_context():
        main_routes.init_routes(app, fake_mongo)
        account_routes.init_routes(app)
        admin_routes.init_routes(app, fake_mongo)
        comment_routes.init_routes(app)
        qr_routes.init_routes(app)
        reset_password_routes.init_routes(app)
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app_sqlite):
    return app_sqlite.test_client()


@pytest.mark.integration
def test_register_and_login_logout(client):
    # register
    resp = client.post(
        "/register",
        data={
            "username": "bob",
            "email": "b@example.com",
            "password": "Secret123!",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302, 303)

    # login
    resp = client.post(
        "/login",
        data={"username": "bob", "password": "Secret123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302, 303)

    # logout
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code in (200, 302, 303)
