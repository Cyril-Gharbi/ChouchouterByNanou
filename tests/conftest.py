import pytest

from app import create_app
from app.models import Admin
from app.models import db as _db


# --- Recording of routes for tests ---
# We make a fake mini "mongo_db" that meets .Prestations.find()
class _FakePrestations:
    def find(self, *args, **kwargs):
        return []


class _FakeMongo:
    Prestations = _FakePrestations()


# Import of route modules and recording on the app
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
            # disable CSRF to simplify potential posts in test
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


@pytest.fixture()
def admin_client(app):
    client = app.test_client()
    # create an admin if not existing
    admin = Admin.query.filter_by(username="admin").first()
    if not admin:
        admin = Admin(username="admin", email="admin@example.com")
        admin.set_password("Admin123!")
        _db.session.add(admin)
        _db.session.commit()
    # admin login
    resp = client.post(
        "/admin/login",
        data={"username": "admin", "password": "Admin123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    return client


@pytest.fixture(autouse=True)
def mail_mock(monkeypatch):
    # Prevents the actual sending of emails during tests
    monkeypatch.setattr("app.utils.mail.send", lambda msg: None)
