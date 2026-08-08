# ==============================================================================
# CyberGuard AI - Frontend API Client
#
# This module is the ONLY place in the Streamlit frontend that talks to the
# network. app.py should never import model.py or utils.py directly anymore -
# every prediction, analytics figure, or safety-guide entry comes through one
# of the functions below, which call the FastAPI backend over HTTP.
#
# Configure the backend location with the BACKEND_URL environment variable,
# e.g. BACKEND_URL=https://your-backend-domain.com
# ==============================================================================
import os
from typing import Dict, List, Optional

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API_BASE = f"{BACKEND_URL}/api/v1"
DEFAULT_TIMEOUT = 15  # seconds


class ApiError(Exception):
    """Raised when the backend returns a structured error response."""

    def __init__(self, code: str, message: str, status_code: int = 0):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{code}] {message}")


def _auth_headers(token: Optional[str] = None) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _request(method: str, path: str, token: Optional[str] = None, **kwargs) -> Dict:
    url = f"{API_BASE}{path}"
    headers = kwargs.pop("headers", {})
    headers.update(_auth_headers(token))
    try:
        resp = requests.request(method, url, headers=headers, timeout=DEFAULT_TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as e:
        raise ApiError("CONNECTION_ERROR", f"Could not reach CyberGuard AI backend at {BACKEND_URL}: {e}")

    try:
        body = resp.json()
    except ValueError:
        raise ApiError("INVALID_RESPONSE", "Backend returned a non-JSON response.", resp.status_code)

    if resp.status_code >= 400 or body.get("success") is False:
        err = body.get("error", {})
        raise ApiError(err.get("code", "UNKNOWN_ERROR"), err.get("message", "Unknown error"), resp.status_code)

    return body


# --------------------------------------------------------------- predictions
def predict_message(text: str, token: Optional[str] = None) -> Dict:
    """Mirrors the original model.predict_message() return shape
    (label, confidence, matched_words, method) plus category/severity,
    which the backend now computes for us."""
    body = _request("POST", "/predict", token=token, json={"text": text})
    data = body["data"]
    return {
        "label": data["label"],
        "confidence": data["confidence"],
        "matched_words": data["matched_words"],
        "method": data["method"],
        "category": data["category"],
        "severity": data["severity"],
    }


def get_prediction_history(token: str, page: int = 1, limit: int = 20) -> Dict:
    return _request("GET", f"/predictions?page={page}&limit={limit}", token=token)


# ------------------------------------------------------------------ analytics
def get_dashboard_stats() -> Dict:
    return _request("GET", "/analytics/dashboard")["data"]


def get_model_analytics() -> Dict:
    return _request("GET", "/analytics/model")["data"]


def get_top_toxic_words(top_n: int = 10) -> List[Dict]:
    return _request("GET", f"/analytics/top-toxic-words?top_n={top_n}")["data"]


# ---------------------------------------------------------------------- model
def get_model_status() -> Dict:
    return _request("GET", "/model/status")["data"]


def retrain_model(admin_token: str) -> Dict:
    return _request("POST", "/model/retrain", token=admin_token)["data"]


# ----------------------------------------------------------------- simulator
def get_simulated_posts() -> List[Dict]:
    return _request("GET", "/simulator/posts")["data"]


def send_chat_message(message: str, token: Optional[str] = None) -> Dict:
    return _request("POST", "/simulator/message", token=token, json={"message": message})


# --------------------------------------------------------------------- safety
def get_safety_tips() -> List[Dict]:
    return _request("GET", "/safety/tips")["data"]


def get_helplines() -> List[Dict]:
    return _request("GET", "/safety/helplines")["data"]


def get_cyber_laws() -> List[Dict]:
    return _request("GET", "/safety/laws")["data"]


def detox_text(text: str, matched_words: List[str]) -> Dict:
    return _request("POST", "/safety/detox", json={"text": text, "matched_words": matched_words})["data"]


# ---------------------------------------------------------------------- auth
def register(username: str, email: str, password: str) -> Dict:
    return _request("POST", "/auth/register", json={"username": username, "email": email, "password": password})


def login(username: str, password: str) -> Dict:
    return _request("POST", "/auth/login", json={"username": username, "password": password})


def health_check() -> Dict:
    return _request("GET", "/health")
