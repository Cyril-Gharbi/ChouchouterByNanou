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
# Mongo (mongomock)
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def mongo_db():
    client = mongomock.MongoClient()
    return client["chouchouter"]


# ------------------------------------------------------------------
# PostgreSQL (pytest-postgresql) ou fallback SQLite
# ------------------------------------------------------------------
try:
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


@pytest.fixture(scope="session")
def pg_app(request):
    """
    Crée une app Flask pour les tests Postgres.
    - Si Postgres est dispo (Linux/CI), utilise pytest-postgresql.
    - Sinon (Windows local), fallback sur SQLite.
    """
    if POSTGRES_AVAILABLE and not sys.platform.startswith("win"):
        postgresql_proc = factories.postgresql_proc()
        uri = postgresql_proc.dsn()
    else:
        # fallback simple sur SQLite
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
