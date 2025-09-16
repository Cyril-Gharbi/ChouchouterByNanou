from datetime import datetime, timezone

import pytest

from app.models import Comment, User


@pytest.mark.integration
def test_postgres_user_insertion(pg_db):
    u = User(username="pguser", email="pg@example.com")
    u.set_password("Secret123!")
    pg_db.session.add(u)
    pg_db.session.commit()
    assert u.id is not None


@pytest.mark.integration
def test_postgres_relations(pg_db):
    u = User(username="rel", email="rel@example.com")
    u.set_password("Secret123!")
    pg_db.session.add(u)
    pg_db.session.commit()

    c = Comment(
        content="Hello",
        username_at_time=u.username,
        user_id=u.id,
        date=datetime.now(timezone.utc),
        is_visible=True,
    )
    pg_db.session.add(c)
    pg_db.session.commit()

    assert c.user_id == u.id
