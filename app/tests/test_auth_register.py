def test_register_user_success(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@test.com",
            "password": "password123",
        },
    )

    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "user1@test.com"
    assert body["role"] == "user"
    assert "id" in body


def test_register_duplicate_email_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "password123",
        },
    )

    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "password123",
        },
    )

    assert r.status_code == 400



def test_register_then_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@test.com",
            "password": "password123",
        },
    )

    r = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@test.com",
            "password": "password123",
        },
    )

    assert r.status_code == 200
    assert "access_token" in r.json()