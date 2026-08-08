def test_register_new_user(client):
    resp = client.post("/api/v1/auth/register", json={
        "username": "newuser1",
        "email": "newuser1@example.com",
        "password": "MyPassword123",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["username"] == "newuser1"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_login_success(client, registered_user):
    resp = client.post("/api/v1/auth/login", json={
        "username": "teststudent",
        "password": "SuperSecret123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_credentials(client, registered_user):
    resp = client.post("/api/v1/auth/login", json={
        "username": "teststudent",
        "password": "WrongPassword",
    })
    assert resp.status_code == 401


def test_protected_endpoint_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_protected_endpoint_with_token(client, registered_user):
    token = registered_user["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "teststudent"


def test_admin_only_retrain_blocked_for_regular_user(client, registered_user):
    token = registered_user["access_token"]
    resp = client.post("/api/v1/model/retrain", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
