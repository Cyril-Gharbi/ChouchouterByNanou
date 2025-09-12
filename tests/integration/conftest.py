import os
import sys
import tempfile

import mongomock
import pytest
from pytest_postgresql import factories

from app import create_app
from app.models import db as _db

# --- ensure project root on sys.path ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ------------------------------------------------------------------
# PostgreSQL (pytest-postgresql) ou fallback SQLite
# ------------------------------------------------------------------
try:
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


@pytest.fixture(scope="session")
def mongo_db():
    """MongoDB mocké disponible pour tous les tests d'intégration."""
    client = mongomock.MongoClient()
    return client["chouchouter"]


@pytest.fixture(scope="session")
def pg_app(request):
    """
    Crée une app Flask pour les tests intégration.
    - Si Postgres dispo (Linux/CI), utilise pytest-postgresql.
    - Sinon (Windows/local), fallback sur SQLite.
    """
    if POSTGRES_AVAILABLE and not sys.platform.startswith("win"):
        postgresql_proc = factories.postgresql_proc()
        uri = postgresql_proc.dsn()
    else:
        uri = "sqlite:///:memory:"

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": uri,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "secret",
            "UPLOAD_FOLDER": tempfile.mkdtemp(),
        }
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def pg_client(pg_app):
    return pg_app.test_client()


@pytest.fixture()
def pg_db(pg_app):
    return _db


@pytest.fixture(scope="function")
def app_mongo(mongo_db):
    """App Flask d'intégration dédiée aux tests MongoDB purs."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "MONGO_DB": mongo_db,
        }
    )
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client_mongo(app_mongo):
    return app_mongo.test_client()
