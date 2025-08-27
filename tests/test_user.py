def test_full_user_flow(client):
    # 1. Inscription
    resp = client.post(
        "/account/register",
        data={
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "Password123!",
        },
    )
    assert resp.status_code in (200, 302)

    # 2. Connexion
    resp = client.post(
        "/account/connection",
        data={"email": "flow@example.com", "password": "Password123!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # 3. Ajout d’un commentaire
    resp = client.post("/comments/add", data={"content": "Excellent service !"})
    assert resp.status_code in (200, 302)

    # 4. Voir mes commentaires
    resp = client.get("/account/my-comments")
    assert resp.status_code == 200
    assert b"Excellent service" in resp.data

    # 5. Suppression de compte
    resp = client.post("/account/delete", follow_redirects=True)
    assert resp.status_code == 200
