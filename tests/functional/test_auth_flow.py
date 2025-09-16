import pytest


@pytest.mark.integration
def test_register_login_logout_flow(client, monkeypatch):
    # Eviter dépendance aux templates
    monkeypatch.setattr("flask.render_template", lambda *a, **k: "OK")

    # Register
    resp = client.post(
        "/register",
        data={
            "username": "bob",
            "email": "b@example.com",
            "password": "Secret123!",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302, 303)

    # Login
    resp = client.post(
        "/login",
        data={"username": "bob", "password": "Secret123!"},
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302, 303)

    # Access account page
    resp = client.get("/connection", follow_redirects=False)
    assert resp.status_code in (200, 302, 303)

    # Logout
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code in (200, 302, 303)
