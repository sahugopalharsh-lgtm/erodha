"""
API integration tests for Django manage.py test runner.
"""

from rest_framework.test import APITestCase
from rest_framework import status


class ApiEndpointsTestCase(APITestCase):
    def test_health_check_endpoint(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")
        self.assertEqual(response.data["quant_engine"], "operational")

    def test_market_data_endpoint(self):
        response = self.client.get("/api/market-data/?symbol=AAPL&period=3mo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("statistics", response.data)
        self.assertIn("calibrated_parameters", response.data)
        self.assertEqual(response.data["symbol"], "AAPL")

    def test_forecast_gbm_endpoint(self):
        payload = {
            "symbol": "AAPL",
            "s0": 150.0,
            "mu": 0.08,
            "sigma": 0.20,
            "horizon_days": 30,
            "n_paths": 500,
            "seed": 42,
        }
        response = self.client.post("/api/forecast/gbm/", data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["model"], "GBM")
        self.assertIn("quantiles", response.data)
        self.assertIn("median", response.data["quantiles"])
        self.assertTrue(len(response.data["sample_paths"]) > 0)

    def test_forecast_merton_endpoint(self):
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
        response = self.client.post("/api/forecast/merton/", data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["model"], "MERTON")
        self.assertIn("quantiles", response.data)
        self.assertIn("terminal", response.data)

    def test_risk_analysis_endpoint(self):
        payload = {
            "symbol": "AAPL",
            "portfolio_value": 50000.0,
            "confidence_level": 0.95,
            "horizon_days": 1,
        }
        response = self.client.post("/api/risk/", data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("historical_risk", response.data)
        self.assertIn("parametric_risk", response.data)
        self.assertGreater(response.data["historical_risk"]["var_95_amount"], 0)

    def test_ipo_analysis_endpoint(self):
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
        response = self.client.post("/api/ipo/", data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("expected_listing_price", response.data)
        self.assertTrue(len(response.data["assumptions"]) > 0)
