def test_admin_access_denied_for_normal_user(client):
    resp = client.get("/admin")
    assert resp.status_code in (302, 403)


def test_admin_dashboard_access(admin_client):
    resp = admin_client.get("/admin")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data
