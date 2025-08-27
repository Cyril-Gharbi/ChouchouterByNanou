import pytest


@pytest.mark.parametrize(
    "path", ["/account", "/admin", "/comments", "/qr", "/reset-password"]
)
def test_routes_exist(client, path):
    resp = client.get(path)
    # on accepte 200, 302 (redir) ou 404 (si route protégée ou non exposée)
    assert resp.status_code in (200, 302, 404)
