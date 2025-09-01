from app.models import User


def _login(client, username="commentuser", password="Password123!"):
    resp = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    return resp


def test_add_comment_success(client, db):
    # utilisateur connecté et approuvé
    u = User(
        username="commentuser",
        firstname="Com",
        lastname="Ment",
        email="comment@example.com",
        is_approved=True,
    )
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    _login(client)

    resp = client.post(
        "/comments", data={"content": "Super prestation !"}, follow_redirects=True
    )
    assert resp.status_code in (200, 302)
    assert b"Commentaire publi" in resp.data or b"Super prestation" in resp.data


def test_add_comment_empty(client, db):
    u = User(
        username="emptyuser",
        firstname="Em",
        lastname="Pty",
        email="empty@example.com",
        is_approved=True,
    )
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    _login(client, "emptyuser")

    resp = client.post("/comments", data={"content": ""}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Commentaires" in resp.data


def test_comment_visibility(client):
    resp = client.get("/comments")
    assert resp.status_code == 200
