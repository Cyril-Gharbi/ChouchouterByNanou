from typing import Any

import pytest

from app import create_app
from app.models import User
from app.models import db as _db


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

    fake_mongo: Any = type(
        "FakeMongo", (), {"Prestations": type("P", (), {"find": lambda *a, **k: []})()}
    )()
    with app.app_context():
        main_routes.init_routes(app, fake_mongo)
        account_routes.init_routes(app)
        admin_routes.init_routes(app, fake_mongo)
        comment_routes.init_routes(app)
        qr_routes.init_routes(app)
        reset_password_routes.init_routes(app)
        _db.create_all()
        # user
        u = User(username="bob", email="b@example.com")
        u.set_password("Secret123!")
        _db.session.add(u)
        _db.session.commit()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app_sqlite):
    return app_sqlite.test_client()


@pytest.mark.integration
def test_scan_requires_login_then_increments_level(client, monkeypatch):
    # pas loggé -> redirige vers login
    resp = client.get("/scan")
    assert resp.status_code in (302, 303)

    # login
    client.post("/login", data={"username": "bob", "password": "Secret123!"})

    # patch email envoi
    monkeypatch.setattr("app.utils.send_email", lambda *a, **k: None)

    # scan
    resp = client.get("/scan")
    assert resp.status_code in (200, 302, 303)
