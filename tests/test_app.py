def test_app_is_created(app):
    assert app is not None


def test_app_has_testing_config(app):
    assert app.config.get("TESTING") is True


def test_index_route(client):
    resp = client.get("/")
    assert resp.status_code in (200, 302)
