"""
Integration tests for Erodha Django REST Framework API
"""

import sys
from pathlib import Path
import os
import django
import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["ERODHA_ALLOW_SYNTHETIC"] = "1"   # tests must run offline; production default is real data only
django.setup()

from rest_framework.test import APIClient
from rest_framework import status


@pytest.fixture
def client():
    return APIClient()


def test_health_check_endpoint(client):
    response = client.get("/api/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "healthy"
    assert response.data["quant_engine"] == "operational"


def test_market_data_endpoint(client):
    response = client.get("/api/market-data/?symbol=AAPL&period=3mo")
    assert response.status_code == status.HTTP_200_OK
    assert "statistics" in response.data
    assert "calibrated_parameters" in response.data
    assert response.data["symbol"] == "AAPL"


def test_forecast_gbm_endpoint(client):
    payload = {
        "symbol": "AAPL",
        "s0": 150.0,
        "mu": 0.08,
        "sigma": 0.20,
        "horizon_days": 30,
        "n_paths": 500,
        "seed": 42,
    }
    response = client.post("/api/forecast/gbm/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["model"] == "GBM"
    assert "quantiles" in response.data
    assert "median" in response.data["quantiles"]
    assert len(response.data["sample_paths"]) > 0


def test_forecast_merton_endpoint(client):
    payload = {
        "symbol": "AAPL",
        "s0": 150.0,
        "mu": 0.08,
        "sigma": 0.18,
        "lam": 2.0,
        "m_j": -0.05,
        "delta_j": 0.10,
        "horizon_days": 30,
        "n_paths": 500,
        "seed": 42,
    }
    response = client.post("/api/forecast/merton/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["model"] == "MERTON"
    assert "quantiles" in response.data
    assert "terminal" in response.data


def test_risk_analysis_endpoint(client):
    payload = {
        "symbol": "AAPL",
        "portfolio_value": 50000.0,
        "confidence_level": 0.95,
        "horizon_days": 1,
    }
    response = client.post("/api/risk/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "historical_risk" in response.data
    assert "parametric_risk" in response.data
    assert response.data["historical_risk"]["var_95_amount"] > 0


def test_ipo_analysis_endpoint(client):
    payload = {
        "company_name": "TestIPO Ltd",
        "symbol": "TEST.IPO",
        "issue_price_min": 100.0,
        "issue_price_max": 105.0,
        "issue_price_final": 105.0,
        "lot_size": 50,
        "issue_size_crores": 500.0,
        "qib_subscription": 30.0,
        "nii_subscription": 15.0,
        "rii_subscription": 5.0,
        "total_subscription": 18.0,
        "grey_market_premium_pct": 25.0,
        "pe_ratio": 22.0,
        "industry_pe": 25.0,
    }
    response = client.post("/api/ipo/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "expected_listing_price" in response.data
    assert len(response.data["assumptions"]) > 0
