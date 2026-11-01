"""
Erodha Frontend: API Client
===========================
Lightweight client consuming the Django REST Framework backend.
Strictly decoupled from quantitative computations.
"""

from typing import Any, Dict, Optional
import requests


class ErodhaAPIClient:
    """Client for the Erodha Django REST API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000/api"):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        """Checks if Django backend is operational."""
        try:
            resp = requests.get(f"{self.base_url}/health/", timeout=3.0)
            if resp.status_code == 200:
                return {"status": "connected", "details": resp.json()}
            return {"status": "error", "message": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "disconnected", "message": str(e)}

    def get_market_data(self, symbol: str = "AAPL", period: str = "1y") -> Dict[str, Any]:
        """Fetches historical price data and descriptive statistics."""
        resp = requests.get(
            f"{self.base_url}/market-data/",
            params={"symbol": symbol, "period": period},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()

    def get_gbm_forecast(
        self,
        symbol: str,
        horizon_days: int = 252,
        n_paths: int = 5000,
        seed: int = 42,
        s0: Optional[float] = None,
        mu: Optional[float] = None,
        sigma: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Requests GBM forecast simulation."""
        payload: Dict[str, Any] = {
            "symbol": symbol,
            "horizon_days": horizon_days,
            "n_paths": n_paths,
            "seed": seed,
        }
        if s0 is not None:
            payload["s0"] = s0
        if mu is not None:
            payload["mu"] = mu
        if sigma is not None:
            payload["sigma"] = sigma

        resp = requests.post(f"{self.base_url}/forecast/gbm/", json=payload, timeout=20.0)
        resp.raise_for_status()
        return resp.json()

    def get_merton_forecast(
        self,
        symbol: str,
        horizon_days: int = 252,
        n_paths: int = 5000,
        seed: int = 42,
        s0: Optional[float] = None,
        mu: Optional[float] = None,
        sigma: Optional[float] = None,
        lam: Optional[float] = None,
        m_j: Optional[float] = None,
        delta_j: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Requests Merton Jump-Diffusion forecast simulation."""
        payload: Dict[str, Any] = {
            "symbol": symbol,
            "horizon_days": horizon_days,
            "n_paths": n_paths,
            "seed": seed,
        }
        if s0 is not None:
            payload["s0"] = s0
        if mu is not None:
            payload["mu"] = mu
        if sigma is not None:
            payload["sigma"] = sigma
        if lam is not None:
            payload["lam"] = lam
        if m_j is not None:
            payload["m_j"] = m_j
        if delta_j is not None:
            payload["delta_j"] = delta_j

        resp = requests.post(f"{self.base_url}/forecast/merton/", json=payload, timeout=20.0)
        resp.raise_for_status()
        return resp.json()

    def get_risk_metrics(
        self,
        symbol: str,
        portfolio_value: float = 100_000.0,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
    ) -> Dict[str, Any]:
        """Requests VaR, Expected Shortfall, and Drawdown analytics."""
        payload = {
            "symbol": symbol,
            "portfolio_value": portfolio_value,
            "confidence_level": confidence_level,
            "horizon_days": horizon_days,
        }
        resp = requests.post(f"{self.base_url}/risk/", json=payload, timeout=60.0)
        resp.raise_for_status()
        return resp.json()

    def get_backtest(
        self,
        symbol: str,
        split_ratio: float = 0.8,
        n_paths: int = 2000,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Requests out-of-sample backtest and Kupiec POF evaluation."""
        payload = {
            "symbol": symbol,
            "split_ratio": split_ratio,
            "n_paths": n_paths,
            "seed": seed,
        }
        resp = requests.post(f"{self.base_url}/backtest/", json=payload, timeout=30.0)
        resp.raise_for_status()
        return resp.json()

    def get_ipo_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Requests IPO pricing and listing gain simulation."""
        resp = requests.post(f"{self.base_url}/ipo/", json=payload, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
