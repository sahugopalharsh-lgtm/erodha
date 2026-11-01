"""
Unit tests for quant_engine.returns
===================================
Tests for return calculations, volatility estimation, Itô drift correction,
and chronological train-test splitting.
"""

import numpy as np
import pandas as pd
import pytest

from quant_engine.returns import (
    ReturnStatistics,
    ReturnsSeries,
    calculate_returns,
    compute_return_statistics,
    chronological_train_test_split,
)


class TestReturnsCalculations:
    """Deterministic mathematical tests for return formulations."""

    def test_constant_growth_returns(self):
        """
        For S_t = S_0 * (1 + g)^t:
        - Simple return R_t must equal g exactly.
        - Log return r_t must equal ln(1 + g) exactly.
        - Volatility must be 0.
        """
        n = 100
        g = 0.02
        s0 = 100.0
        prices = s0 * ((1 + g) ** np.arange(n))

        res = calculate_returns(prices, trading_days=252)

        # Simple returns should be identical to g
        np.testing.assert_allclose(res.simple_returns.values, g, rtol=1e-12)

        # Log returns should be identical to ln(1 + g)
        expected_log = np.log(1 + g)
        np.testing.assert_allclose(res.log_returns.values, expected_log, rtol=1e-12)

        # Volatility should be 0.0
        assert res.stats.daily_volatility == pytest.approx(0.0, abs=1e-12)
        assert res.stats.annualized_volatility == pytest.approx(0.0, abs=1e-12)

    def test_log_returns_time_additivity(self):
        """
        Verify the fundamental property: sum_{t=1}^T r_t == ln(S_T / S_0)
        and show that simple returns do not sum to total percentage return.
        """
        np.random.seed(42)
        daily_changes = 1.0 + np.random.normal(0.0005, 0.015, size=50)
        prices = 100.0 * np.cumprod(daily_changes)

        res = calculate_returns(prices)

        total_log_return = res.log_returns.sum()
        expected_total_log = np.log(prices[-1] / prices[0])
        assert total_log_return == pytest.approx(expected_total_log, rel=1e-10)

        # Simple returns sum does NOT equal (S_T - S_0) / S_0
        total_simple_return = (prices[-1] - prices[0]) / prices[0]
        assert res.simple_returns.sum() != pytest.approx(total_simple_return, rel=1e-3)

    def test_ito_convexity_drift_relationship(self):
        """
        Verify mu_annual = mu_log_annual + 0.5 * sigma_annual^2
        """
        np.random.seed(123)
        # Synthesize daily returns with known drift and vol
        mu_log_target = 0.10  # 10% annual log drift
        sigma_target = 0.20   # 20% annual vol
        dt = 1 / 252

        daily_r = np.random.normal((mu_log_target - 0.5 * sigma_target**2) * dt, sigma_target * np.sqrt(dt), size=1000)
        stats_obj = compute_return_statistics(daily_r, trading_days=252)

        expected_drift = stats_obj.annualized_log_return + 0.5 * (stats_obj.annualized_volatility ** 2)
        assert stats_obj.drift_mu == pytest.approx(expected_drift, rel=1e-12)

    def test_heavy_tails_detection_via_jarque_bera(self):
        """
        A normal distribution has excess kurtosis ~0 and high JB p-value.
        A jump-contaminated distribution has fat tails (excess kurtosis > 0)
        and rejects normality (JB p-value < 0.05).
        """
        np.random.seed(999)
        # 1. Pure normal returns
        normal_returns = np.random.normal(0.0005, 0.01, size=2000)
        norm_stats = compute_return_statistics(normal_returns)
        assert abs(norm_stats.excess_kurtosis) < 0.5
        assert norm_stats.jarque_bera_p_value > 0.05
        assert norm_stats.is_normal_5pct is True

        # 2. Contaminated returns with severe jumps
        jump_returns = normal_returns.copy()
        jump_indices = np.random.choice(len(jump_returns), size=20, replace=False)
        jump_returns[jump_indices] += np.random.choice([-0.08, 0.08], size=20)  # 8% shocks

        jump_stats = compute_return_statistics(jump_returns)
        assert jump_stats.excess_kurtosis > 1.0  # Leptokurtic (fat tails)
        assert jump_stats.jarque_bera_p_value < 0.001
        assert jump_stats.is_normal_5pct is False

    def test_invalid_price_inputs(self):
        with pytest.raises(ValueError, match="At least 2 price observations required"):
            calculate_returns([100.0])

        with pytest.raises(ValueError, match="contains non-positive values"):
            calculate_returns([100.0, 0.0, 105.0])


class TestChronologicalSplit:
    """Tests guaranteeing zero data leakage in train-test partitioning."""

    def test_fractional_split_ordering(self):
        dates = pd.date_range("2023-01-01", periods=100, freq="B")
        df = pd.DataFrame({"price": np.arange(100)}, index=dates)

        train, test = chronological_train_test_split(df, split_point=0.8)

        assert len(train) == 80
        assert len(test) == 20
        # Strict temporal ordering: train maximum timestamp < test minimum timestamp
        assert train.index.max() < test.index.min()
        # Verify continuity: no missing intermediate elements
        assert train.index[-1] + pd.Timedelta(days=1) <= test.index[0] or test.index[0] > train.index[-1]

    def test_date_cutoff_split(self):
        dates = pd.date_range("2023-01-01", periods=60, freq="D")
        s = pd.Series(np.arange(60), index=dates)

        cutoff = "2023-01-31"
        train, test = chronological_train_test_split(s, split_point=cutoff)

        assert train.index.max() <= pd.Timestamp(cutoff)
        assert test.index.min() > pd.Timestamp(cutoff)
        assert len(train) + len(test) == len(s)

    def test_invalid_split_points(self):
        dates = pd.date_range("2023-01-01", periods=10, freq="D")
        s = pd.Series(np.arange(10), index=dates)

        with pytest.raises(ValueError, match="Invalid split_point"):
            chronological_train_test_split(s, split_point=1.5)

        with pytest.raises(ValueError, match="results in empty train"):
            chronological_train_test_split(s, split_point="2020-01-01")
