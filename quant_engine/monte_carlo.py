"""
Erodha Quantitative Engine: Monte Carlo Simulation Engine
=========================================================
Unified multi-path simulation, quantile cones, and convergence diagnostics.

Key Features:
- Vectorized path simulations for GBM and Merton Jump-Diffusion.
- Quantile trajectories across time: 5%, 25%, 50% (median), 75%, 95%.
- Sample trajectory selection for visual inspection.
- Monte Carlo convergence metrics and Standard Error of the Mean:
  SE(mean) = std(S_T) / sqrt(M)
  95% MC Confidence Interval for Mean = mean(S_T) +/- 1.96 * SE(mean)
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple, Union
import numpy as np

from quant_engine.gbm import GBMSimulationResult, simulate_gbm_paths
from quant_engine.jump_diffusion import MertonSimulationResult, simulate_merton_paths


@dataclass(frozen=True)
class ForecastDistribution:
    """Predictive trajectory distributions and terminal scenario outcomes."""
    model_type: Literal["GBM", "MERTON"]
    s0: float
    horizon_years: float
    n_steps: int
    n_paths: int
    dt: float
    time_grid: np.ndarray             # (n_steps + 1,)
    
    # Quantile cones across time (n_steps + 1,)
    q05_path: np.ndarray
    q25_path: np.ndarray
    median_path: np.ndarray
    q75_path: np.ndarray
    q95_path: np.ndarray
    mean_path: np.ndarray

    # Terminal metrics at horizon T
    terminal_prices: np.ndarray       # (n_paths,)
    terminal_mean: float
    terminal_median: float
    terminal_std: float
    terminal_q05: float
    terminal_q25: float
    terminal_q75: float
    terminal_q95: float
    
    # Monte Carlo precision
    mc_standard_error: float          # std / sqrt(M)
    mc_mean_ci_95: Tuple[float, float]
    
    # Representative sample paths for plotting (e.g. 25 paths)
    sample_paths: np.ndarray          # (n_steps + 1, min(n_paths, n_samples))


def run_monte_carlo_forecast(
    model: Literal["GBM", "MERTON"],
    s0: float,
    mu: float,
    sigma: float,
    horizon_days: int = 252,
    trading_days: int = 252,
    n_paths: int = 5000,
    n_steps: Optional[int] = None,
    lam: float = 0.0,
    m_j: float = 0.0,
    delta_j: float = 0.0,
    seed: Optional[int] = 42,
    n_sample_trajectories: int = 25,
) -> ForecastDistribution:
    """
    Executes a high-performance Monte Carlo forecast simulation.

    Parameters
    ----------
    model : "GBM" or "MERTON"
        Stochastic model to execute.
    s0 : float
        Starting asset price.
    mu : float
        Annualized drift rate.
    sigma : float
        Annualized volatility.
    horizon_days : int
        Forecast horizon in trading days (default: 252).
    trading_days : int
        Annualization factor (default: 252).
    n_paths : int
        Number of simulation paths (default: 5000).
    n_steps : Optional[int]
        Number of simulation steps (defaults to horizon_days).
    lam, m_j, delta_j : float
        Merton jump parameters (ignored if model == "GBM").
    seed : Optional[int]
        Reproducible PRNG seed.
    n_sample_trajectories : int
        Number of individual path traces to save for visualization.

    Returns
    -------
    ForecastDistribution
    """
    horizon_years = float(horizon_days / trading_days)
    steps = n_steps if n_steps is not None else horizon_days

    if model.upper() == "GBM":
        sim_res = simulate_gbm_paths(
            s0=s0,
            mu=mu,
            sigma=sigma,
            horizon_years=horizon_years,
            n_steps=steps,
            n_paths=n_paths,
            seed=seed,
        )
    elif model.upper() == "MERTON":
        sim_res = simulate_merton_paths(
            s0=s0,
            mu=mu,
            sigma=sigma,
            lam=lam,
            m_j=m_j,
            delta_j=delta_j,
            horizon_years=horizon_years,
            n_steps=steps,
            n_paths=n_paths,
            seed=seed,
        )
    else:
        raise ValueError(f"Unknown model '{model}'. Supported: 'GBM', 'MERTON'.")

    paths = sim_res.paths  # shape: (steps + 1, n_paths)
    terminal = paths[-1, :]

    # Compute quantile paths across each time step
    q05 = np.percentile(paths, 5, axis=1)
    q25 = np.percentile(paths, 25, axis=1)
    q50 = np.percentile(paths, 50, axis=1)
    q75 = np.percentile(paths, 75, axis=1)
    q95 = np.percentile(paths, 95, axis=1)
    mean_p = np.mean(paths, axis=1)

    # Terminal statistics
    t_mean = float(np.mean(terminal))
    t_median = float(np.median(terminal))
    t_std = float(np.std(terminal, ddof=1))
    t_q05 = float(np.percentile(terminal, 5))
    t_q25 = float(np.percentile(terminal, 25))
    t_q75 = float(np.percentile(terminal, 75))
    t_q95 = float(np.percentile(terminal, 95))

    # Monte Carlo standard error of the mean
    se_mean = float(t_std / np.sqrt(n_paths))
    ci_lower = t_mean - 1.96 * se_mean
    ci_upper = t_mean + 1.96 * se_mean

    # Extract sample paths for visualization
    sample_count = min(n_paths, n_sample_trajectories)
    sample_paths = paths[:, :sample_count]

    return ForecastDistribution(
        model_type=model.upper(),  # type: ignore
        s0=s0,
        horizon_years=horizon_years,
        n_steps=steps,
        n_paths=n_paths,
        dt=sim_res.dt,
        time_grid=sim_res.time_grid,
        q05_path=q05,
        q25_path=q25,
        median_path=q50,
        q75_path=q75,
        q95_path=q95,
        mean_path=mean_p,
        terminal_prices=terminal,
        terminal_mean=t_mean,
        terminal_median=t_median,
        terminal_std=t_std,
        terminal_q05=t_q05,
        terminal_q25=t_q25,
        terminal_q75=t_q75,
        terminal_q95=t_q95,
        mc_standard_error=se_mean,
        mc_mean_ci_95=(ci_lower, ci_upper),
        sample_paths=sample_paths,
    )
