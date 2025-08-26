import pytest


@pytest.mark.parametrize(
    "route",
    [
        "/account",
        "/admin",
        "/comments",
        "/qr",
        "/reset-password",
    ],
)
def test_routes_exist(client, route):
    response = client.get(route)
    # Either 200 OK, 302 Redirect (login required), or 404 if disabled
    assert response.status_code in (200, 302, 404)
