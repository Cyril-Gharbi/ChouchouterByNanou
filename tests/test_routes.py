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
        "/delete_account",
        "/admin/login",
        "/admin/dashboard",
        "/scan",
        "/reset_user_password",  # return 403 expected without token
        "/reset_user_request",
    ],
)
def test_routes_exist(client, path, monkeypatch):
    if path == "/rates":

        def fake_render(*args, **kwargs):
            return "Page des tarifs OK"

        monkeypatch.setattr("flask.render_template", fake_render)

    resp = client.get(path)
    assert resp.status_code in (200, 302, 403)
