"""
Unit tests for quant_engine.jump_diffusion
==========================================
Deterministic tests for Merton Jump-Diffusion simulation and drift compensator.
"""

import numpy as np
import pytest

from quant_engine.gbm import simulate_gbm_paths
from quant_engine.jump_diffusion import calculate_jump_compensator, simulate_merton_paths


class TestMertonJumpDiffusion:
    """Verifies theoretical stochastic properties of the Merton simulator."""

    def test_lambda_zero_reduces_to_gbm(self):
        """When lambda = 0, Merton paths are identical to GBM paths with the same seed."""
        s0 = 100.0
        mu = 0.08
        sigma = 0.20
        t = 0.5
        n_steps = 100
        n_paths = 200
        seed = 42

        gbm_res = simulate_gbm_paths(s0=s0, mu=mu, sigma=sigma, horizon_years=t, n_steps=n_steps, n_paths=n_paths, seed=seed)
        merton_res = simulate_merton_paths(
            s0=s0, mu=mu, sigma=sigma, lam=0.0, m_j=0.0, delta_j=0.0,
            horizon_years=t, n_steps=n_steps, n_paths=n_paths, seed=seed
        )

        np.testing.assert_allclose(merton_res.paths, gbm_res.paths, rtol=1e-12)
        assert merton_res.total_jumps_simulated == 0

    def test_zero_jump_size_eliminates_jump_effect(self):
        """When m_j = 0 and delta_j = 0, jump magnitude is zero, compensator kappa = 0."""
        kappa = calculate_jump_compensator(m_j=0.0, delta_j=0.0)
        assert kappa == pytest.approx(0.0, abs=1e-12)

    def test_drift_compensator_expectation(self):
        """
        Terminal sample mean E[S_T] must converge to S_0 * exp(mu * T)
        even in the presence of jumps due to drift compensation -lambda * kappa * dt.
        """
        s0 = 100.0
        mu = 0.06
        sigma = 0.15
        lam = 2.0         # 2 jumps per year on average
        m_j = -0.05       # 5% downward average jump
        delta_j = 0.10    # 10% jump volatility
        t = 1.0
        m = 25_000
        seed = 777

        res = simulate_merton_paths(
            s0=s0, mu=mu, sigma=sigma, lam=lam, m_j=m_j, delta_j=delta_j,
            horizon_years=t, n_steps=252, n_paths=m, seed=seed
        )

        terminal = res.paths[-1, :]
        sample_mean = float(np.mean(terminal))
        theo_mean = res.theoretical_mean
        se = float(np.std(terminal, ddof=1) / np.sqrt(m))

        assert abs(sample_mean - theo_mean) < 3.0 * se
        assert res.total_jumps_simulated > 0
