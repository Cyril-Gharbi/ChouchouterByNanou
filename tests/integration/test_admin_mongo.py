import pytest

from app import create_app
from app.models import Admin
from app.models import db as _db

# On réutilise la fixture mongo_db fournie
# par tests/integration/conftest_mongo.py (mongomock)


@pytest.fixture(scope="function")
def app_mongo(mongo_db):
    """Application Flask configurée avec SQLite en mémoire
    + routes enregistrées avec un mongo_db (mongomock)."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,  # simplifie les POST de login
        }
    )

    # Enregistrement des routes avec le mongo_db simulé
    from app.routes import (
        account_routes,
        admin_routes,
        comment_routes,
        main_routes,
        qr_routes,
        reset_password_routes,
    )

    with app.app_context():
        main_routes.init_routes(app, mongo_db)
        account_routes.init_routes(app)
        admin_routes.init_routes(app, mongo_db)
        comment_routes.init_routes(app)
        qr_routes.init_routes(app)
        reset_password_routes.init_routes(app)

        _db.create_all()

        # Création d'un admin pour le login
        admin = Admin(username="admin", email="admin@example.com")
        admin.set_password("Admin123!")
        _db.session.add(admin)
        _db.session.commit()

        yield app

        _db.drop_all()


@pytest.fixture()
def client_mongo(app_mongo):
    return app_mongo.test_client()


@pytest.mark.integration
def test_admin_dashboard_access_and_mongo_usage(client_mongo, mongo_db, monkeypatch):
    """
    Vérifie qu'un admin connecté peut accéder à /admin/dashboard
    et que la route utilise bien MongoDB.
    On insère un doc dans mongo_db.Prestations
    et on s'assure que la route ne plante pas.
    """

    # Évite les dépendances aux templates Jinja :
    # on remplace render_template par une fonction simple
    def fake_render_template(*args, **kwargs):
        return "OK"

    monkeypatch.setattr("flask.render_template", fake_render_template)
    # Évite l'envoi d'e-mails
    monkeypatch.setattr("app.utils.mail.send", lambda msg: None)

    # Préparer des données Mongo (Prestation)
    mongo_db.Prestations.insert_one(
        {
            "category": "Extension",
            "name": "Soin du visage",
            "description": "masque beauté",
            "price": "49",
            "order": 1,
        }
    )

    # Login admin
    resp = client_mongo.post(
        "/admin/login",
        data={"username": "admin", "password": "Admin123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)

    # Accès au dashboard
    resp = client_mongo.get("/admin/dashboard")
    assert resp.status_code == 200
