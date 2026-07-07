"""Scan history router tests (no live Supabase project required).

Without SUPABASE_JWT_SECRET configured, every request is treated as
anonymous, so these endpoints must consistently require auth (401).
"""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

VALID_BODY = {
    "measurement": {
        "length_mm": 260.0,
        "width_mm": 98.0,
        "confidence": 0.9,
        "method": "manual-cm",
    },
    "goals": {
        "sport": "running",
        "surface": "road",
        "cushioning": "balanced",
        "use_case": "daily",
    },
    "recommendations": [],
}


def test_save_scan_requires_auth():
    r = client.post("/scans", json=VALID_BODY)
    assert r.status_code == 401


def test_list_scans_requires_auth():
    r = client.get("/scans")
    assert r.status_code == 401


def test_delete_scan_requires_auth():
    r = client.delete("/scans/some-id")
    assert r.status_code == 401


def test_bogus_bearer_token_is_rejected():
    r = client.get("/scans", headers={"Authorization": "Bearer not-a-real-jwt"})
    assert r.status_code == 401
