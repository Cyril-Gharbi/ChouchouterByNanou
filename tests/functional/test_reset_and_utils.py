from typing import Any

import pytest

from app import create_app
from app.models import Admin, User
from app.models import db as _db
from app.utils import (
    generate_password_reset_token,
    verifier_email,
    verify_password_reset_token,
)


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

        u = User(username="bob", firstname="B", lastname="O", email="b@example.com")
        u.set_password("Secret123!")
        _db.session.add(u)
        a = Admin(username="admin", email="a@example.com")
        a.set_password("Admin123!")
        _db.session.add(a)

        _db.session.commit()

        yield app
        _db.drop_all()


@pytest.fixture()
def client(app_sqlite):
    return app_sqlite.test_client()


@pytest.mark.integration
def test_user_reset_token_and_flow(client, monkeypatch):
    # utils
    t = generate_password_reset_token("b@example.com", "user")
    assert verify_password_reset_token(t) == ("b@example.com", "user")

    # mock send mail
    monkeypatch.setattr("app.utils.mail.send", lambda msg: None)

    # request reset
    resp = client.post(
        "/reset_user_request", data={"email": "b@example.com"}, follow_redirects=False
    )
    assert resp.status_code in (200, 302, 303)

    # use token
    resp = client.post(
        "/reset_user_password?token=" + t,
        data={"password": "NewPw123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302, 303)


@pytest.mark.integration
def test_admin_reset_token_and_flow(client, monkeypatch):
    t = generate_password_reset_token("a@example.com", "admin")
    assert verify_password_reset_token(t) == ("a@example.com", "admin")

    monkeypatch.setattr("app.utils.mail.send", lambda msg: None)

    resp = client.post(
        "/admin/reset_password", data={"email": "a@example.com"}, follow_redirects=False
    )
    assert resp.status_code in (200, 302, 303)

    resp = client.post(
        "/admin/reset_token/" + t,
        data={"password": "AdminNew123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302, 303)


@pytest.mark.integration
def test_verifier_email():
    with pytest.raises(ValueError):
        verifier_email("invalid-email")
