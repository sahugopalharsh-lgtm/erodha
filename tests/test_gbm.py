"""
Unit tests for quant_engine.gbm
===============================
Deterministic mathematical tests for Geometric Brownian Motion simulation.
"""

import numpy as np
import pytest

from quant_engine.gbm import simulate_gbm_paths


class TestGBMSimulation:
    """Verifies theoretical stochastic properties of the GBM simulator."""

    def test_positive_prices(self):
        """GBM prices must be strictly positive at all times (exponential nature)."""
        res = simulate_gbm_paths(s0=100.0, mu=0.08, sigma=0.25, horizon_years=1.0, n_steps=252, n_paths=500, seed=42)
        assert (res.paths > 0).all()

    def test_reproducibility_with_seed(self):
        """Simulations with identical seeds must generate bit-for-bit identical paths."""
        res1 = simulate_gbm_paths(s0=100.0, mu=0.05, sigma=0.2, horizon_years=0.5, n_steps=50, n_paths=100, seed=123)
        res2 = simulate_gbm_paths(s0=100.0, mu=0.05, sigma=0.2, horizon_years=0.5, n_steps=50, n_paths=100, seed=123)
        np.testing.assert_array_equal(res1.paths, res2.paths)

    def test_zero_volatility_limit(self):
        """When sigma = 0, price evolution is purely deterministic: S_t = S_0 * exp(mu * t)."""
        s0 = 100.0
        mu = 0.10
        t = 1.0
        n_steps = 100
        res = simulate_gbm_paths(s0=s0, mu=mu, sigma=0.0, horizon_years=t, n_steps=n_steps, n_paths=10, seed=42)

        expected_terminal = s0 * np.exp(mu * t)
        np.testing.assert_allclose(res.paths[-1, :], expected_terminal, rtol=1e-10)

    def test_expectation_convergence_within_tolerance(self):
        """
        Terminal sample mean must converge to theoretical E[S_T] = S_0 * exp(mu * T)
        within 3 Monte Carlo standard errors: |mean - theo| < 3 * (std / sqrt(M)).
        """
        s0 = 100.0
        mu = 0.08
        sigma = 0.20
        t = 1.0
        m = 20_000
        res = simulate_gbm_paths(s0=s0, mu=mu, sigma=sigma, horizon_years=t, n_steps=252, n_paths=m, seed=999)

        terminal = res.paths[-1, :]
        sample_mean = float(np.mean(terminal))
        theo_mean = res.theoretical_mean
        se = float(np.std(terminal, ddof=1) / np.sqrt(m))

        assert abs(sample_mean - theo_mean) < 3.0 * se
