def test_dashboard_stats_structure(client):
    resp = client.get("/api/v1/analytics/dashboard")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "model_accuracy" in data
    assert "messages_scanned" in data
    assert "safe_messages" in data
    assert "cyberbullying_detected" in data


def test_dashboard_stats_increment_after_prediction(client):
    before = client.get("/api/v1/analytics/dashboard").json()["data"]["messages_scanned"]
    client.post("/api/v1/predict", json={"text": "This is a perfectly nice message"})
    after = client.get("/api/v1/analytics/dashboard").json()["data"]["messages_scanned"]
    assert after == before + 1


def test_model_analytics_endpoint(client):
    resp = client.get("/api/v1/analytics/model")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "model_type" in data
    assert "trained" in data


def test_prediction_history_isolated_per_user(client):
    client.post("/api/v1/auth/register", json={
        "username": "userA", "email": "userA@example.com", "password": "PasswordA123"
    })
    login_a = client.post("/api/v1/auth/login", json={"username": "userA", "password": "PasswordA123"})
    token_a = login_a.json()["access_token"]

    client.post("/api/v1/auth/register", json={
        "username": "userB", "email": "userB@example.com", "password": "PasswordB123"
    })
    login_b = client.post("/api/v1/auth/login", json={"username": "userB", "password": "PasswordB123"})
    token_b = login_b.json()["access_token"]

    client.post("/api/v1/predict", json={"text": "Hello from user A"},
                headers={"Authorization": f"Bearer {token_a}"})

    history_b = client.get("/api/v1/predictions", headers={"Authorization": f"Bearer {token_b}"})
    assert history_b.status_code == 200
    assert history_b.json()["data"] == []

    history_a = client.get("/api/v1/predictions", headers={"Authorization": f"Bearer {token_a}"})
    assert len(history_a.json()["data"]) >= 1
