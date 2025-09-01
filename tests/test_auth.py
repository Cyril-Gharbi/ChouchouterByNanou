from app.models import User


def test_register_success(client, db):
    resp = client.post(
        "/register",
        data={
            "username": "newuser",
            "firstname": "Test",
            "lastname": "User",
            "email": "newuser@example.com",
            "password": "Password123!",
            "consent_privacy": "on",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303, 200)
    u = User.query.filter_by(email="newuser@example.com").first()
    assert u is not None
    assert u.is_approved is False  # l'inscription demande validation admin


def test_register_missing_consent_redirects(client):
    resp = client.post(
        "/register",
        data={
            "username": "badconsent",
            "firstname": "No",
            "lastname": "Consent",
            "email": "bad@example.com",
            "password": "Password123!",
            # pas de consent_privacy
        },
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)


def test_login_success(client, db):
    # Crée un utilisateur approuvé
    u = User(
        username="loginuser",
        firstname="Login",
        lastname="User",
        email="login@example.com",
        is_approved=True,
    )
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    resp = client.post(
        "/login",
        data={"username": "loginuser", "password": "Password123!"},
        follow_redirects=False,
    )
    # devrait rediriger vers /connection
    assert resp.status_code in (302, 303)
    assert "/connection" in (resp.location or "")


def test_login_wrong_password(client, db):
    u = User(
        username="wrongpass",
        firstname="Wrong",
        lastname="Pass",
        email="wrongpass@example.com",
        is_approved=True,
    )
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    resp = client.post(
        "/login",
        data={"username": "wrongpass", "password": "incorrect"},
        follow_redirects=False,
    )

    # L’appli redirige vers /connection
    assert resp.status_code == 302
    assert "/connection" in resp.headers["Location"]
