import datetime
import os
import sys
from typing import Any

import pytest

from app import create_app
from app.models import Admin
from app.models import db as _db

# --- ensure project root on sys.path ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# --- Faux Mongo minimal pour enregistrer les routes qui en dépendent ---
class _FakePrestations:
    def find(self, *args, **kwargs):
        return []


class _FakeMongo:
    Prestations = _FakePrestations()


def _register_routes(app):
    from app.routes import (
        account_routes,
        admin_routes,
        comment_routes,
        main_routes,
        qr_routes,
        reset_password_routes,
    )

    fake_mongo: Any = _FakeMongo()
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
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "secret",
        }
    )
    with app.app_context():
        _register_routes(app)
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_client(client, db):
    """Client déjà connecté en admin (création + login)."""
    username = "admin"
    email = "admin@example.com"
    password = "Admin123!"

    if not Admin.query.filter_by(username=username).first():
        admin = Admin(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

    # login par username (fallback sur email si besoin)
    resp = client.post(
        "/admin/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    if resp.status_code not in (302, 303):
        resp = client.post(
            "/admin/login",
            data={"email": email, "password": password},
            follow_redirects=False,
        )

    assert resp.status_code in (302, 303)
    return client


@pytest.fixture(autouse=True)
def mail_mock(monkeypatch):
    # Empêche l'envoi réel d'e-mails
    monkeypatch.setattr("app.utils.mail.send", lambda msg: None)


@pytest.fixture
def username():
    return "admin"


@pytest.fixture
def email():
    return "admin@example.com"


@pytest.fixture
def firstname():
    return "Alice"


@pytest.fixture
def lastname():
    return "Martin"


@pytest.fixture
def content():
    return "Hello world"


@pytest.fixture
def username_at_time():
    return "admin@t0"


@pytest.fixture
def user_id():
    return 1


@pytest.fixture
def date():
    return datetime.date.today()


@pytest.fixture
def is_visible():
    return True
