def test_reset_password_flow(client):
    # Demande de reset
    resp = client.post("/reset-password/request", data={"email": "login@example.com"})
    assert resp.status_code in (200, 302)

    # Ici il faudrait mocker la génération et l’envoi du token
    token = "fake-token"

    # Utilisation du token
    resp = client.post(
        f"/reset-password/form/{token}", data={"password": "NewPassword123!"}
    )
    assert resp.status_code in (200, 302)
