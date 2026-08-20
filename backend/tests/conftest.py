import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["DATABASE_URL"] = "sqlite:///./test_cyberguard.db"
os.environ["STORE_PREDICTION_TEXT"] = "true"

import pytest
from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("test_cyberguard.db")
    except OSError:
        pass


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def registered_user(client):
    resp = client.post("/api/v1/auth/register", json={
        "username": "teststudent",
        "email": "teststudent@example.com",
        "password": "SuperSecret123",
    })
    body = resp.json()
    if not body.get("success") and body.get("error", {}).get("code") == "USER_EXISTS":
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "teststudent",
            "password": "SuperSecret123",
        })
        return login_resp.json()
    return body
