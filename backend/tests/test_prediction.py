def test_predict_safe_text(client):
    resp = client.post("/api/v1/predict", json={"text": "Good morning everyone, have a great day!"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["label"] in (0, 1)
    assert "confidence" in data
    assert "matched_words" in data
    assert "method" in data
    assert "category" in data
    assert "severity" in data


def test_predict_bullying_text(client):
    resp = client.post("/api/v1/predict", json={"text": "You are so stupid and ugly, everyone hates you"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["label"] == 1
    assert data["is_cyberbullying"] is True
    assert data["prediction"] == "Cyberbullying"


def test_predict_empty_text_rejected(client):
    resp = client.post("/api/v1/predict", json={"text": ""})
    assert resp.status_code in (400, 422)


def test_predict_very_long_text_rejected(client):
    long_text = "a " * 5000
    resp = client.post("/api/v1/predict", json={"text": long_text})
    assert resp.status_code == 422


def test_predict_response_structure(client):
    resp = client.post("/api/v1/predict", json={"text": "Have a nice day"})
    data = resp.json()["data"]
    expected_keys = {
        "label", "is_cyberbullying", "prediction", "confidence",
        "confidence_percent", "matched_words", "method", "category",
        "severity", "disclaimer",
    }
    assert expected_keys.issubset(data.keys())


def test_model_status_endpoint(client):
    resp = client.get("/api/v1/model/status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "model_loaded" in data
    assert "model_type" in data
    assert "fallback_available" in data
