from datetime import datetime, timezone

from app.models import Comment, User


def test_create_user(db):
    u = User(
        username="testuser",
        firstname="Test",
        lastname="User",
        email="test@example.com",
    )
    u.set_password("password123!")  # password_hash est NOT NULL dans le modèle
    db.session.add(u)
    db.session.commit()
    assert u.id is not None


def test_create_comment(db):
    c = Comment(
        content="Hello world",
        username_at_time="testuser",  # NOT NULL dans le modèle
        date=datetime.now(timezone.utc),
        is_visible=True,
    )
    db.session.add(c)
    db.session.commit()
    assert c.id is not None
