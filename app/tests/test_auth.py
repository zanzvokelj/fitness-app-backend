import pytest


# =========================
# REGISTER
# =========================

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
    assert r.json()["detail"] == "Email already registered"


# =========================
# LOGIN
# =========================

def test_login_success(client):
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
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "fail@test.com",
            "password": "password123",
        },
    )

    r = client.post(
        "/api/v1/auth/login",
        data={
            "username": "fail@test.com",
            "password": "WRONG",
        },
    )

    assert r.status_code == 401


# =========================
# /ME
# =========================

def test_me_returns_current_user(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@test.com",
            "password": "password123",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "me@test.com",
            "password": "password123",
        },
    )

    token = login.json()["access_token"]

    r = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "me@test.com"
    assert body["role"] == "user"


def test_me_without_token_fails(client):
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401

# =========================
# REFRESH TOKEN
# =========================

def test_refresh_token_works(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@test.com",
            "password": "password123",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "refresh@test.com",
            "password": "password123",
        },
    )

    old_refresh = login.json()["refresh_token"]

    r = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )

    assert r.status_code == 200
    body = r.json()

    assert "access_token" in body
    assert "refresh_token" in body
    assert body["refresh_token"] != old_refresh


def test_refresh_token_cannot_be_reused(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "reuse@test.com",
            "password": "password123",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "reuse@test.com",
            "password": "password123",
        },
    )

    old_refresh = login.json()["refresh_token"]

    # first refresh OK
    r1 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert r1.status_code == 200

    # second refresh with same token MUST FAIL
    r2 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert r2.status_code == 401


def test_refresh_with_invalid_token_fails(client):
    r = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )

    assert r.status_code == 401

# =========================
# LOGOUT
# =========================

def test_logout_revokes_refresh_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout@test.com",
            "password": "password123",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "logout@test.com",
            "password": "password123",
        },
    )

    refresh_token = login.json()["refresh_token"]

    # logout
    r = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert r.status_code == 200

    # refresh should now FAIL
    r2 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert r2.status_code == 401