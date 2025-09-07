def test_admin_access_denied_for_normal_user(client):
    resp = client.get("/admin/dashboard", follow_redirects=False)
    # not connected -> redirection to /admin/login
    assert resp.status_code in (302, 303)
    assert "/admin/login" in (resp.location or "")


def test_admin_dashboard_access(admin_client):
    resp = admin_client.get("/admin/dashboard")
    # The dashboard must be accessible once logged in
    assert resp.status_code == 200
