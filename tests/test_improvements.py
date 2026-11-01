"""Tests for MLE calibration, horizon-aware risk, and real-data-by-default behaviour."""
import os
import numpy as np
import pandas as pd
import pytest

from quant_engine.jump_diffusion import simulate_merton_paths
from quant_engine.estimation import estimate_model_parameters, estimate_merton_mle
from quant_engine.risk import horizon_returns_from_daily, compute_empirical_var_es
from quant_engine.gbm import simulate_gbm_paths


def test_mle_recovers_jump_parameters_on_average():
    true = dict(mu=0.12, sigma=0.18, lam=4.0, m_j=-0.04, delta_j=0.05)
    est = []
    for seed in range(12):
        p = simulate_merton_paths(100, true["mu"], true["sigma"], true["lam"], true["m_j"],
                                  true["delta_j"], 5, 1260, 1, seed=seed).paths[:, 0]
        e = estimate_merton_mle(p)
        est.append((e.sigma_continuous, e.lam, e.m_j, e.delta_j))
    sigma, lam, m_j, delta = np.mean(est, axis=0)
    assert sigma == pytest.approx(0.18, abs=0.02)
    assert lam == pytest.approx(4.0, abs=1.5)
    assert m_j == pytest.approx(-0.04, abs=0.03)
    assert delta == pytest.approx(0.05, abs=0.03)


def test_mle_fixes_not_worsens_lambda_vs_threshold():
    errs_t, errs_m = [], []
    for seed in range(12):
        p = simulate_merton_paths(100, 0.1, 0.18, 4.0, -0.04, 0.05, 5, 1260, 1, seed=seed).paths[:, 0]
        errs_t.append(abs(estimate_model_parameters(p).lam - 4.0))
        errs_m.append(abs(estimate_merton_mle(p).lam - 4.0))
    assert np.mean(errs_m) <= np.mean(errs_t) + 0.5


def test_horizon_returns_change_var():
    p = simulate_gbm_paths(100, 0.1, 0.25, 3, 756, 1, seed=3).paths[:, 0]
    daily = pd.Series(p).pct_change().dropna().values
    v1 = compute_empirical_var_es(daily, 0.95).var_percentage
    v10 = compute_empirical_var_es(horizon_returns_from_daily(daily, 10), 0.95, horizon_days=10).var_percentage
    assert v10 > v1 * 1.8   # roughly sqrt(10) ~ 3.2x for iid returns


def test_horizon_needs_enough_data():
    with pytest.raises(ValueError):
        horizon_returns_from_daily(np.random.normal(0, 0.01, 40), 30)


def test_real_data_is_default_no_silent_synthetic(monkeypatch):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
    from api import market_data_service as m

    class Boom:
        def __init__(self, *a, **k): pass
        def history(self, *a, **k): raise RuntimeError("no network")
    monkeypatch.setattr(m.yf, "Ticker", Boom)
    monkeypatch.delenv("ERODHA_ALLOW_SYNTHETIC", raising=False)
    with pytest.raises(RuntimeError):
        m.fetch_historical_prices("RELIANCE.NS")
    monkeypatch.setenv("ERODHA_ALLOW_SYNTHETIC", "1")
    _, _, _, synth = m.fetch_historical_prices("RELIANCE.NS")
    assert synth is True
