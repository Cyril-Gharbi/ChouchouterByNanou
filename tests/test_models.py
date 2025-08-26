from app.models import Comment, User


def test_create_user(db):
    user = User(username="testuser", email="test@example.com")
    db.session.add(user)
    db.session.commit()
    assert user.id is not None


def test_create_comment(db):
    comment = Comment(content="Hello world")
    db.session.add(comment)
    db.session.commit()
    assert comment.id is not None
