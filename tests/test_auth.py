def test_register_success(client):
    resp = client.post(
        "/account/register",
        data={
            "username": "newuser",
            "firstname": "Test",
            "lastname": "User",
            "email": "newuser@example.com",
            "password": "Password123!",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Bienvenue" in resp.data or b"Connexion" in resp.data


def test_register_invalid_email(client):
    resp = client.post(
        "/account/register",
        data={
            "username": "bademail",
            "email": "not-an-email",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 400 or b"erreur" in resp.data.lower()


def test_login_success(client):
    client.post(
        "/account/register",
        data={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Password123!",
        },
    )
    resp = client.post(
        "/account/connection",
        data={"email": "login@example.com", "password": "Password123!"},
    )
    assert resp.status_code in (200, 302)


def test_login_wrong_password(client):
    resp = client.post(
        "/account/connection",
        data={"email": "login@example.com", "password": "wrongpass"},
    )
    assert resp.status_code in (401, 200)
    assert b"incorrect" in resp.data.lower() or b"erreur" in resp.data.lower()
