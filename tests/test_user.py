from app.models import User


def _login(client, username, password):
    resp = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    return resp


def test_full_user_flow(client, db):
    # Création d'un utilisateur approuvé
    u = User(
        username="flowuser",
        firstname="Flow",
        lastname="User",
        email="flow@example.com",
        is_approved=True,
    )
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    # Connexion
    _login(client, "flowuser", "Password123!")

    # Ajout d’un commentaire
    resp = client.post(
        "/comments", data={"content": "Excellent service !"}, follow_redirects=True
    )
    assert resp.status_code in (200, 302)

    # Voir les commentaires
    resp = client.get("/comments")
    assert resp.status_code == 200
    assert b"Excellent service" in resp.data or b"Commentaires" in resp.data

    # Suppression de compte (mot de passe requis)
    resp = client.post(
        "/delete_account", data={"password": "Password123!"}, follow_redirects=False
    )
    assert resp.status_code in (302, 303, 200)
