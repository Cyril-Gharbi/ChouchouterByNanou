from app.models import User
from app.utils import generate_password_reset_token


def test_reset_password_flow(client, db):
    # Create an approved user
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

    # Generate a token and open the reset page
    token = generate_password_reset_token("reset@example.com", "user")
    resp = client.get(f"/reset_user_password?token={token}")
    assert resp.status_code in (200, 302)

    # Send the new password on the same URL
    resp = client.post(
        f"/reset_user_password?token={token}",
        data={"password": "NewPassword123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303, 200)

    # Check that we can log in with the new password
    resp = client.post(
        "/login",
        data={"username": "resetuser", "password": "NewPassword123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
