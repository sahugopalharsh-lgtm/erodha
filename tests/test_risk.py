"""
Unit tests for quant_engine.risk
================================
Deterministic tests for Value at Risk, Expected Shortfall, and Maximum Drawdown.
"""

import numpy as np
import pytest

from quant_engine.risk import (
    calculate_maximum_drawdown,
    compute_empirical_var_es,
    compute_parametric_var_es,
)


class TestRiskMetrics:
    """Verifies risk metric properties and estimators."""

    def test_parametric_matches_theory(self):
        """For N(0, 0.01^2), VaR_95 = 1.64485 * 0.01 = 0.0164485."""
        mu = 0.0
        sigma = 0.01
        res = compute_parametric_var_es(mean_return=mu, volatility=sigma, confidence_level=0.95, portfolio_value=100_000.0)

        expected_var_pct = 1.6448536269514722 * sigma
        assert res.var_percentage == pytest.approx(expected_var_pct, rel=1e-4)
        assert res.var_amount == pytest.approx(100_000.0 * expected_var_pct, rel=1e-4)
        # Expected Shortfall must be strictly greater than VaR
        assert res.es_percentage > res.var_percentage
        assert res.es_amount > res.var_amount

    def test_empirical_var_monotonicity(self):
        """VaR at 99% must be greater than or equal to VaR at 95%."""
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, size=10_000)

        var_95 = compute_empirical_var_es(returns, confidence_level=0.95)
        var_99 = compute_empirical_var_es(returns, confidence_level=0.99)

        assert var_99.var_percentage > var_95.var_percentage
        assert var_95.es_percentage > var_95.var_percentage
        assert var_99.es_percentage > var_99.var_percentage

    def test_maximum_drawdown_known_sequence(self):
        """Test on known price drop: peak 100, drops to 70, recovers to 90 -> MDD = 30%."""
        prices = [100.0, 90.0, 70.0, 85.0, 90.0]
        mdd = calculate_maximum_drawdown(prices)
        assert mdd == pytest.approx(0.30, abs=1e-6)

        # Monotonically increasing prices has MDD = 0
        increasing_prices = [10.0, 20.0, 30.0, 40.0]
        assert calculate_maximum_drawdown(increasing_prices) == pytest.approx(0.0, abs=1e-6)
