"""
Erodha Quantitative Engine: Parameter Estimation Module
=======================================================
Estimation of continuous diffusion and discontinuous jump parameters
from historical asset price series.

Methodology:
1. Geometric Brownian Motion (GBM):
   - Sample mean daily log return: r_bar
   - Daily volatility: s_daily
   - Annualized volatility: sigma_gbm = s_daily * sqrt(tau)
   - Annualized arithmetic drift: mu_gbm = r_bar * tau + 0.5 * sigma_gbm^2

2. Merton Jump-Diffusion (Threshold & Robust MAD Decomposition):
   - Robust median and Median Absolute Deviation (MAD):
     sigma_robust = 1.4826 * median( |r_t - median(r)| )
   - Threshold cutoff = k * sigma_robust (default k = 3.0 stds)
   - Jump classification: |r_t - median(r)| > cutoff
   - Jump frequency (Poisson intensity): lambda = (n_jumps / N) * tau
   - Log-jump distribution:
     m_j = mean(r_jumps), delta_j = std(r_jumps)
   - Continuous diffusion volatility:
     sigma_cont = std(r_non_jumps) * sqrt(tau)
   - Drift compensator:
     kappa = exp(m_j + 0.5 * delta_j^2) - 1
   - Total arithmetic drift:
     mu = r_bar * tau + 0.5 * (sigma_gbm^2)
"""

from dataclasses import dataclass
from typing import Optional, Union
import numpy as np
import pandas as pd

from quant_engine.returns import ReturnsSeries, calculate_returns


@dataclass(frozen=True)
class ModelParameters:
    """Estimated parameters for both GBM and Merton Jump-Diffusion."""
    symbol: str
    sample_size: int
    trading_days: int
    threshold_sigma: float
    
    # GBM Parameters
    mu_gbm: float
    sigma_gbm: float
    
    # Merton Parameters
    mu_merton: float
    sigma_continuous: float
    lam: float
    m_j: float
    delta_j: float
    kappa: float
    jump_count: int
    jump_fraction: float


def estimate_model_parameters(
    data: Union[pd.Series, np.ndarray, ReturnsSeries],
    symbol: str = "ASSET",
    trading_days: int = 252,
    jump_threshold_stds: float = 3.0,
) -> ModelParameters:
    """
    Estimates GBM and Merton Jump-Diffusion parameters from price or return series.

    Parameters
    ----------
    data : pd.Series, np.ndarray, or ReturnsSeries
        Historical prices or return object.
    symbol : str
        Ticker symbol identifier.
    trading_days : int
        Annualization factor (default: 252).
    jump_threshold_stds : float
        Multiple of robust standard deviation to classify jump shocks (default: 3.0).

    Returns
    -------
    ModelParameters
        Calibrated parameters ready for stochastic simulation.
    """
    if isinstance(data, ReturnsSeries):
        log_ret = data.log_returns.values
        stats_obj = data.stats
    elif isinstance(data, (pd.Series, np.ndarray, list)):
        arr = np.asarray(data, dtype=np.float64)
        if (arr > 0).all() and len(arr) > 2 and np.any(np.diff(arr) != 0):
            # Assume it's a price series
            ret_series = calculate_returns(arr, trading_days=trading_days)
            log_ret = ret_series.log_returns.values
            stats_obj = ret_series.stats
        else:
            raise ValueError("Data must be a valid positive price series or ReturnsSeries.")
    else:
        raise ValueError(f"Unsupported data type for parameter estimation: {type(data).__name__}")

    n = len(log_ret)
    if n < 10:
        raise ValueError(f"At least 10 return observations required for calibration; got {n}.")

    # 1. GBM Calibration
    sigma_gbm = stats_obj.annualized_volatility
    mu_gbm = stats_obj.drift_mu

    # 2. Merton Jump Calibration via Robust MAD Thresholding
    median_ret = float(np.median(log_ret))
    mad = float(np.median(np.abs(log_ret - median_ret)))
    # Normal consistency factor 1.4826 for MAD
    robust_sigma_daily = max(1e-6, 1.4826 * mad)
    cutoff = jump_threshold_stds * robust_sigma_daily

    jump_mask = np.abs(log_ret - median_ret) > cutoff
    n_jumps = int(np.sum(jump_mask))
    jump_fraction = float(n_jumps / n)

    # Annualized jump intensity lambda
    lam = float((n_jumps / n) * trading_days)

    if n_jumps >= 2:
        jump_returns = log_ret[jump_mask]
        m_j = float(np.mean(jump_returns))
        delta_j = float(np.std(jump_returns, ddof=1))
        # Ensure delta_j is strictly non-zero
        delta_j = max(1e-4, delta_j)
    elif n_jumps == 1:
        jump_returns = log_ret[jump_mask]
        m_j = float(jump_returns[0])
        delta_j = 0.02
    else:
        # Zero jumps observed
        m_j = 0.0
        delta_j = 0.01
        lam = 0.0

    # Compensator kappa = exp(m_j + 0.5 * delta_j^2) - 1
    kappa = float(np.exp(m_j + 0.5 * (delta_j ** 2)) - 1.0)

    # Continuous diffusion volatility estimated from non-jump returns
    non_jump_returns = log_ret[~jump_mask]
    if len(non_jump_returns) >= 2:
        continuous_daily_std = float(np.std(non_jump_returns, ddof=1))
        sigma_continuous = continuous_daily_std * np.sqrt(trading_days)
    else:
        sigma_continuous = sigma_gbm

    # Total expected arithmetic return rate matches empirical asset drift
    mu_merton = mu_gbm

    return ModelParameters(
        symbol=symbol,
        sample_size=n,
        trading_days=trading_days,
        threshold_sigma=jump_threshold_stds,
        mu_gbm=mu_gbm,
        sigma_gbm=sigma_gbm,
        mu_merton=mu_merton,
        sigma_continuous=sigma_continuous,
        lam=lam,
        m_j=m_j,
        delta_j=delta_j,
        kappa=kappa,
        jump_count=n_jumps,
        jump_fraction=jump_fraction,
    )


# ---------------------------------------------------------------------------
# Maximum-likelihood calibration of the Merton model
# ---------------------------------------------------------------------------
from scipy import optimize, stats as _stats  # noqa: E402


def _merton_neg_loglik(theta, r, dt, k_max=6):
    """Negative log-likelihood of daily log returns under Merton.

    r_t ~ sum_k Poisson(k; lam*dt) * N(a*dt + k*m_j, sigma^2*dt + k*delta^2)
    theta = (a, sigma, lam, m_j, delta); `a` is the diffusion log-drift per year.
    """
    a, sigma, lam, m_j, delta = theta
    if sigma <= 1e-6 or delta <= 1e-6 or lam < 0:
        return 1e12
    ks = np.arange(0, k_max + 1)
    w = _stats.poisson.pmf(ks, lam * dt)                      # (K,)
    mean = a * dt + ks * m_j                                  # (K,)
    std = np.sqrt(sigma ** 2 * dt + ks * delta ** 2)          # (K,)
    dens = (w[None, :] * _stats.norm.pdf(r[:, None], mean[None, :], std[None, :])).sum(axis=1)
    return float(-np.sum(np.log(np.maximum(dens, 1e-300))))


def estimate_merton_mle(
    data: Union[pd.Series, np.ndarray, ReturnsSeries],
    symbol: str = "ASSET",
    trading_days: int = 252,
) -> ModelParameters:
    """Calibrate Merton jump-diffusion by maximum likelihood.

    Starts from the threshold (MAD) estimate and refines with L-BFGS-B.
    Falls back to the threshold estimate if the optimiser fails.
    Returns the same ModelParameters container as `estimate_model_parameters`.
    """
    base = estimate_model_parameters(data, symbol=symbol, trading_days=trading_days)
    if isinstance(data, ReturnsSeries):
        r = data.log_returns.values
    else:
        r = calculate_returns(np.asarray(data, dtype=np.float64), trading_days=trading_days).log_returns.values
    dt = 1.0 / trading_days

    lam0 = max(base.lam, 1.0)
    x0 = np.array([
        float(np.mean(r)) * trading_days - lam0 * base.m_j,
        max(base.sigma_continuous, 0.05),
        lam0,
        base.m_j if base.jump_count else -0.02,
        max(base.delta_j, 0.02),
    ])
    bounds = [(-2.0, 2.0), (0.01, 2.0), (0.0, 100.0), (-0.5, 0.5), (0.005, 0.5)]
    res = optimize.minimize(_merton_neg_loglik, x0, args=(r, dt), method="L-BFGS-B", bounds=bounds)
    if not res.success and not np.isfinite(res.fun):
        return base

    a, sigma, lam, m_j, delta = [float(v) for v in res.x]
    kappa = float(np.exp(m_j + 0.5 * delta ** 2) - 1.0)
    mu = float(a + lam * kappa + 0.5 * sigma ** 2)   # arithmetic drift consistent with the simulator
    return ModelParameters(
        symbol=symbol,
        sample_size=base.sample_size,
        trading_days=trading_days,
        threshold_sigma=base.threshold_sigma,
        mu_gbm=base.mu_gbm,
        sigma_gbm=base.sigma_gbm,
        mu_merton=mu,
        sigma_continuous=sigma,
        lam=lam,
        m_j=m_j,
        delta_j=delta,
        kappa=kappa,
        jump_count=base.jump_count,
        jump_fraction=base.jump_fraction,
    )
