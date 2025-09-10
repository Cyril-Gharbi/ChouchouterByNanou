import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/portfolio",
        "/rates",
        "/comments",
        "/connection",
        "/cgu",
        "/mentions",
        "/politique",
        "/contact",
        "/register",
        "/login",
        "/logout",
        "/admin/login",
        "/admin/dashboard",
        "/reset_user_password",  # sans token => 403 attendu
        "/reset_user_request",
    ],
)
def test_routes_exist(client, path, monkeypatch):
    # Certaines routes appellent un template spécifique -> on neutralise
    if path == "/rates":
        monkeypatch.setattr("flask.render_template", lambda *a, **k: "OK")

    resp = client.get(path)
    assert resp.status_code in (200, 302, 303, 403)


def test_app_is_created(app):
    assert app is not None


def test_app_has_testing_config(app):
    assert app.config.get("TESTING") is True
