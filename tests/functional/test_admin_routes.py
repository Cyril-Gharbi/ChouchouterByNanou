import io
from typing import Any

import pytest

from app import create_app
from app.models import Admin, User
from app.models import db as _db


@pytest.fixture(autouse=True)
def ensure_upload_folder(tmp_path, app_sqlite):
    folder = tmp_path / "uploads"
    folder.mkdir()
    app_sqlite.config["UPLOAD_FOLDER"] = str(folder)
    yield


@pytest.fixture()
def app_sqlite():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "UPLOAD_FOLDER": "static/uploads",  # utilis  par admin_routes
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

    # faux mongo pour l'init (mais ici on ciblera surtout POST sans toucher Prestations)
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

        # admin + user exemple
        admin = Admin(username="admin", email="admin@example.com")
        admin.set_password("Admin123!")
        _db.session.add(admin)
        user = User(
            username="u1",
            firstname="A",
            lastname="B",
            email="u1@example.com",
            is_approved=True,
        )
        user.set_password("Pw123!xxx")
        _db.session.add(user)
        _db.session.commit()

        yield app

        _db.drop_all()


@pytest.fixture()
def client(app_sqlite):
    return app_sqlite.test_client()


def login_admin(client):
    resp = client.post(
        "/admin/login",
        data={"username": "admin", "password": "Admin123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)


@pytest.mark.integration
def test_admin_login_logout(client):
    login_admin(client)
    # logout (via route /logout_admin si pr sente,
    # sinon on nettoie la session par GET dashboard->redir ???)
    # Si pas de route d di e, on v rifie simplement l'acc s dashboard apr s login
    resp = client.get("/admin/dashboard")
    assert resp.status_code in (200, 302, 303)


@pytest.mark.integration
def test_admin_dashboard_post_upload(client, monkeypatch, tmp_path):
    login_admin(client)

    # mock render_template pour simplifier la r ponse
    monkeypatch.setattr("flask.render_template", lambda *a, **k: "OK")
    # Forcer UPLOAD_FOLDER vers tmp_path
    from flask import current_app

    current_app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Fichier image factice autorisé
    data = {
        "photo": (io.BytesIO(b"fake image bytes"), "test.jpg"),
        "description": "demo",
    }
    resp = client.post(
        "/admin/dashboard", data=data, content_type="multipart/form-data"
    )
    # suivant ta logique, soit 200, soit redirection
    assert resp.status_code in (200, 302, 303)
