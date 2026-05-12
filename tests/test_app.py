"""
Tests for StockAnalyze Flask application.
"""
import json
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ── Page routes ──────────────────────────────────────────────────────────────

def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"StockAnalyze" in res.data
    assert b"^GSPC" in res.data  # S&P 500


def test_macro_page(client):
    res = client.get("/macro")
    assert res.status_code == 200
    assert b"^TNX" in res.data   # 10Y UST indicator
    assert b"^VIX" in res.data   # VIX


def test_charts_page(client):
    res = client.get("/charts")
    assert res.status_code == 200
    assert b"candlestick" in res.data.lower() or b"K" in res.data


def test_learn_page(client):
    res = client.get("/learn")
    assert res.status_code == 200
    # Should have both video and article resources
    assert b"YouTube" in res.data
    assert b"Investopedia" in res.data


def test_advisor_page(client):
    res = client.get("/advisor")
    assert res.status_code == 200
    assert b"Conservative" in res.data
    assert b"Moderate" in res.data
    assert b"Aggressive" in res.data


# ── API endpoints ────────────────────────────────────────────────────────────

def test_advisor_api_moderate(client):
    payload = {"risk": "moderate", "horizon": "long", "amount": 10000, "assets": ["us"]}
    res = client.post("/api/advisor-analysis",
                      data=json.dumps(payload),
                      content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert "profile" in data
    assert "insights" in data
    assert data["profile"]["name"] == "稳健型 Moderate"


def test_advisor_api_conservative(client):
    payload = {"risk": "conservative", "horizon": "short", "amount": 500, "assets": []}
    res = client.post("/api/advisor-analysis",
                      data=json.dumps(payload),
                      content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["profile"]["risk_level"] == "低"
    # Short horizon insight
    assert any("短线" in i for i in data["insights"])


def test_advisor_api_aggressive(client):
    payload = {"risk": "aggressive", "horizon": "long", "amount": 200000, "assets": ["crypto", "china"]}
    res = client.post("/api/advisor-analysis",
                      data=json.dumps(payload),
                      content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["profile"]["risk_level"] == "高"
    # Large amount insight
    assert any("分批" in i for i in data["insights"])
    # Crypto insight
    assert any("加密" in i for i in data["insights"])
    # China insight
    assert any("中国" in i for i in data["insights"])


def test_advisor_api_unknown_risk_defaults_to_moderate(client):
    payload = {"risk": "unknown_type", "horizon": "medium", "amount": 10000, "assets": []}
    res = client.post("/api/advisor-analysis",
                      data=json.dumps(payload),
                      content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["profile"]["name"] == "稳健型 Moderate"


def test_chart_api_invalid_ticker(client):
    """Invalid/unavailable ticker should return 404 or error JSON."""
    res = client.get("/api/chart/INVALIDTICKER999?period=5d")
    # Either 404 (empty data) or 500 (network error in sandbox)
    assert res.status_code in (404, 500)
    data = res.get_json()
    assert "error" in data


def test_macro_chart_api_invalid_ticker(client):
    res = client.get("/api/macro-chart/INVALIDTICKER999?period=6mo")
    assert res.status_code in (404, 500)
    data = res.get_json()
    assert "error" in data


def test_static_css(client):
    res = client.get("/static/css/style.css")
    assert res.status_code == 200
    assert b"--accent" in res.data


def test_static_js(client):
    res = client.get("/static/js/main.js")
    assert res.status_code == 200
