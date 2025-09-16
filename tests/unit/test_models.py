from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Comment, User


def test_create_user(db):
    u = User(
        username="testuser",
        email="testuser@example.com",
    )
    u.set_password("password123!")
    db.session.add(u)
    db.session.commit()
    assert u.id is not None


def test_create_comment(db):
    # We first create a user so that the comment is linked to someone
    user = User(
        username="commenter1",
        email="commenter1@example.com",
    )
    user.set_password("password123!")
    db.session.add(user)
    db.session.commit()

    c = Comment(
        content="Hello world",
        username_at_time=user.username,
        user_id=user.id,
        date=datetime.now(timezone.utc),
        is_visible=True,
    )
    db.session.add(c)
    db.session.commit()
    assert c.id is not None


def test_unique_email(db):
    """Un email doit être unique"""
    u1 = User(username="user1", email="unique1@example.com")
    u1.set_password("password123!")
    db.session.add(u1)
    db.session.commit()

    u2 = User(username="user2", email="unique1@example.com")
    u2.set_password("password456!")
    db.session.add(u2)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_comment_linked_to_user(db):
    """Un commentaire doit être lié à un utilisateur existant"""
    user = User(
        username="commenter2",
        email="commenter2@example.com",
    )
    user.set_password("password123!")
    db.session.add(user)
    db.session.commit()

    comment = Comment(
        content="Test comment",
        username_at_time=user.username,
        user_id=user.id,
        date=datetime.now(timezone.utc),
        is_visible=True,
    )
    db.session.add(comment)
    db.session.commit()

    assert comment.user_id == user.id


def test_required_field_email(db):
    """Un utilisateur sans email ne peut pas être créé (email NOT NULL)"""
    u = User(username="nouser", email=None)
    u.set_password("password123!")
    db.session.add(u)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
