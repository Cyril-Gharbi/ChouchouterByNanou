def test_app_is_created(app):
    assert app is not None


def test_app_has_testing_config(app):
    assert app.config["TESTING"] is True


def test_index_route(client):
    response = client.get("/")
    assert response.status_code in (200, 302)
