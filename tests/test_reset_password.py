from app.models import User
from app.utils import generate_password_reset_token


def test_reset_password_flow(client, db):
    # Crée un user approuvé
    u = User(
        username="resetuser",
        firstname="Re",
        lastname="Set",
        email="reset@example.com",
        is_approved=True,
    )
    u.set_password("OldPass123!")
    db.session.add(u)
    db.session.commit()

    # Génère un token et ouvre la page de reset
    token = generate_password_reset_token("reset@example.com", "user")
    resp = client.get(f"/reset_user_password?token={token}")
    assert resp.status_code in (200, 302)

    # Envoie le nouveau mot de passe sur la même URL
    resp = client.post(
        f"/reset_user_password?token={token}",
        data={"password": "NewPassword123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303, 200)

    # Vérifie qu'on peut se connecter avec le nouveau mot de passe
    resp = client.post(
        "/login",
        data={"username": "resetuser", "password": "NewPassword123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
