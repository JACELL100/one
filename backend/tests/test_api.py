"""FastAPI contract tests via TestClient."""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_catalog_lists_products():
    r = client.get("/catalog")
    assert r.status_code == 200
    products = r.json()["products"]
    assert len(products) >= 6
    assert all("id" in p and "name" in p for p in products)


def test_manual_measurement_endpoint():
    r = client.post("/scan/foot/manual", json={"length_cm": 26.0})
    assert r.status_code == 200
    body = r.json()
    assert body["measurement"]["length_mm"] == 260.0
    assert body["manual_fallback_recommended"] is False


def test_size_endpoint_and_unknown_product():
    ok = client.post("/size", json={"length_mm": 258.0, "product_id": "one8-velocity-pro"})
    assert ok.status_code == 200
    assert ok.json()["fit"] in {"snug", "true", "roomy"}

    missing = client.post("/size", json={"length_mm": 258.0, "product_id": "nope"})
    assert missing.status_code == 404


def test_recommend_endpoint():
    payload = {
        "length_mm": 260.0,
        "goals": {"sport": "running", "surface": "road", "cushioning": "plush", "use_case": "daily"},
        "limit": 3,
    }
    r = client.post("/recommend", json=payload)
    assert r.status_code == 200
    recs = r.json()["recommendations"]
    assert len(recs) == 3
    assert all(0.0 <= x["match_score"] <= 1.0 for x in recs)


def test_gait_endpoint():
    r = client.post("/scan/gait", params={"pronation_deg": 10.0})
    assert r.status_code == 200
    assert r.json()["gait_profile"] == "stability"


def test_scan_foot_empty_upload_rejected():
    files = {"image": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
    r = client.post("/scan/foot", files=files)
    assert r.status_code == 400
