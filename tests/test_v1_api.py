"""Tests for the /api/v1 adapter used by the React dashboard (offline, synthetic data)."""
import os, sys
from pathlib import Path
import django, pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["ERODHA_ALLOW_SYNTHETIC"] = "1"
django.setup()
from rest_framework.test import APIClient


@pytest.fixture
def c():
    return APIClient()


def test_stock_detail_shape(c):
    r = c.get("/api/v1/stocks/RELIANCE")
    assert r.status_code == 200
    d = r.json()
    for k in ["symbol", "currentPrice", "volatility", "var95", "jumpFrequency", "meanJumpSize", "beta", "isDemo"]:
        assert k in d
    assert d["isDemo"] is True  # offline test run: flagged as synthetic


def test_history_has_forecast_and_ma(c):
    d = c.get("/api/v1/stocks/TCS/history?timeframe=3M").json()
    assert len(d["historical"]) == 66 and len(d["forecast"]) == 30
    assert d["forecast"][0]["confidenceLower"] <= d["forecast"][0]["confidenceUpper"]


def test_forecast_bands_ordered(c):
    d = c.post("/api/v1/forecast", {"symbol": "INFY", "horizonDays": 30}, format="json").json()
    assert d["lowerBound"] < d["medianTargetPrice"] < d["upperBound"]
    assert len(d["quantileBands"]) == 30


def test_monte_carlo_and_override(c):
    d = c.post("/api/v1/simulations/monte-carlo",
               {"symbol": "TCS", "numSimulations": 500, "horizonDays": 20, "jumpLambda": 0}, format="json").json()
    assert d["parametersUsed"]["lambda"] == 0.0
    assert len(d["summaryCurve"]) == 21 and d["finalLower5"] < d["finalUpper95"]


def test_risk_horizon_changes_var(c):
    a = c.post("/api/v1/risk", {"symbol": "HDFCBANK", "horizonDays": 1}, format="json").json()
    b = c.post("/api/v1/risk", {"symbol": "HDFCBANK", "horizonDays": 10}, format="json").json()
    assert b["var95Pct"] > a["var95Pct"]
    assert a["riskLevel"] in {"LOW", "MODERATE", "HIGH", "EXTREME"} and a["returnDistribution"]


def test_ipo(c):
    body = {"companyName": "X", "sector": "IT", "priceBandMin": 450, "priceBandMax": 500, "lotSize": 30,
            "issueSizeCr": 1500, "peRatio": 30, "sectorPe": 28, "greyMarketPremium": 100,
            "retailSubscriptionMultiple": 12, "qibSubscriptionMultiple": 25, "niiSubscriptionMultiple": 10}
    d = c.post("/api/v1/ipo/analyze", body, format="json").json()
    assert len(d["scenarios"]) == 3 and d["minimumInvestmentPerLot"] == 15000
