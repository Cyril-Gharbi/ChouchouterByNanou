def test_add_comment_success(client):
    client.post(
        "/account/register",
        data={
            "username": "commentuser",
            "email": "comment@example.com",
            "password": "Password123!",
        },
    )
    client.post(
        "/account/connection",
        data={"email": "comment@example.com", "password": "Password123!"},
    )
    resp = client.post("/comments/add", data={"content": "Super prestation !"})
    assert resp.status_code in (200, 302)


def test_add_comment_empty(client):
    resp = client.post("/comments/add", data={"content": ""})
    assert resp.status_code in (400, 200)
    assert b"vide" in resp.data.lower()


def test_comment_visibility(client):
    resp = client.get("/comments")
    assert resp.status_code == 200
    assert b"Commentaires" in resp.data
