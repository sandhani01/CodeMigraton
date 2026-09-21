import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("[OK] Health check passed.")

def test_analyze_breaking_change():
    payload = {
        "code": "from django.utils.timezone import utc\nnow = utc",
        "library": "django",
        "from_version": "4.0",
        "to_version": "5.1"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["findings"]) > 0
    finding = data["findings"][0]
    assert finding["status"] == "VERIFIED"
    assert finding["symbol"] == "django.utils.timezone.utc"
    assert finding["change_type"] in ["removed", "deprecated"]
    assert len(finding["citations"]) > 0
    assert "https://" in finding["citations"][0]["source_url"]
    print(f"[OK] Breaking change analysis passed: detected {finding['symbol']} with {len(finding['citations'])} verified citations.")

def test_analyze_url_routing():
    payload = {
        "code": "from django.conf.urls import url\nurlpatterns = [url(r'^home/$', home)]",
        "library": "django",
        "from_version": "3.2",
        "to_version": "5.1"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["findings"]) > 0
    assert any("django.conf.urls.url" in f["symbol"] for f in data["findings"])
    print("[OK] URL routing migration test passed.")

def test_grounding_rule_clean_code():
    payload = {
        "code": "from django.core.cache import cache\nres = cache.get('key')",
        "library": "django",
        "from_version": "4.0",
        "to_version": "5.1"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    for f in data["findings"]:
        assert f["status"] == "UNVERIFIED" or f["change_type"] in ["none", "not_affected"]
    print("[OK] Grounding rule test passed: strictly no hallucinated breaking changes.")

if __name__ == "__main__":
    print("Running automated test suite...")
    test_health_check()
    test_analyze_breaking_change()
    test_analyze_url_routing()
    test_grounding_rule_clean_code()
    print("ALL TESTS PASSED SUCCESSFULLY!")
