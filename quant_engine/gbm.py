"""
Erodha Quantitative Engine: Geometric Brownian Motion (GBM)
===========================================================
Stochastic modeling of asset prices under continuous diffusion.

Stochastic Differential Equation (SDE):
    dS_t = mu * S_t dt + sigma * S_t dW_t

By Itô's Lemma for X_t = ln(S_t):
    d(ln S_t) = (mu - 0.5 * sigma^2) dt + sigma dW_t

Exact Discrete Time-Step Simulation:
    S_{t + dt} = S_t * exp( (mu - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z )
    where Z ~ N(0, 1)

Analytical Moments:
    E[S_T] = S_0 * exp(mu * T)
    Var[S_T] = S_0^2 * exp(2 * mu * T) * (exp(sigma^2 * T) - 1)
    Median[S_T] = S_0 * exp( (mu - 0.5 * sigma^2) * T )
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class GBMSimulationResult:
    """Container holding simulated price paths and theoretical moments."""
    paths: np.ndarray             # shape: (n_steps + 1, n_paths)
    time_grid: np.ndarray         # shape: (n_steps + 1,)
    s0: float
    mu: float
    sigma: float
    horizon_years: float
    n_paths: int
    dt: float
    theoretical_mean: float
    theoretical_variance: float
    theoretical_median: float


def simulate_gbm_paths(
    s0: float,
    mu: float,
    sigma: float,
    horizon_years: float,
    n_steps: int,
    n_paths: int,
    seed: Optional[int] = None,
) -> GBMSimulationResult:
    """
    Simulates exact sample paths for Geometric Brownian Motion.

    Parameters
    ----------
    s0 : float
        Initial asset price (must be > 0).
    mu : float
        Annualized expected arithmetic drift.
    sigma : float
        Annualized diffusion volatility (must be >= 0).
    horizon_years : float
        Forecast horizon in years (T > 0).
    n_steps : int
        Number of discrete time steps.
    n_paths : int
        Number of Monte Carlo paths.
    seed : Optional[int]
        Random seed for exact reproducibility.

    Returns
    -------
    GBMSimulationResult
        Container with simulated paths (shape: (n_steps + 1, n_paths))
        and theoretical moments.
    """
    if s0 <= 0:
        raise ValueError(f"Initial price s0 must be strictly positive; got {s0}.")
    if sigma < 0:
        raise ValueError(f"Volatility sigma must be non-negative; got {sigma}.")
    if horizon_years <= 0:
        raise ValueError(f"Horizon must be strictly positive; got {horizon_years}.")
    if n_steps <= 0 or n_paths <= 0:
        raise ValueError(f"n_steps and n_paths must be positive integers.")

    dt = horizon_years / n_steps
    time_grid = np.linspace(0.0, horizon_years, n_steps + 1)

    # Initialize random generator
    rng = np.random.default_rng(seed)

    # Generate standard normal increments Z ~ N(0, 1)
    z = rng.standard_normal(size=(n_steps, n_paths))

    # Continuous drift component per time step: (mu - 0.5 * sigma^2) * dt
    drift_step = (mu - 0.5 * (sigma ** 2)) * dt
    diffusion_step = sigma * np.sqrt(dt) * z

    # Log increments
    log_increments = drift_step + diffusion_step

    # Cumulative sum of log increments
    log_paths = np.vstack([np.zeros((1, n_paths)), np.cumsum(log_increments, axis=0)])

    # Exponentiate and scale by s0: S_t = S_0 * exp(sum(d ln S))
    paths = s0 * np.exp(log_paths)

    # Theoretical moments at terminal horizon T
    theo_mean = s0 * np.exp(mu * horizon_years)
    theo_var = (s0 ** 2) * np.exp(2 * mu * horizon_years) * (np.exp((sigma ** 2) * horizon_years) - 1.0)
    theo_median = s0 * np.exp((mu - 0.5 * (sigma ** 2)) * horizon_years)

    return GBMSimulationResult(
        paths=paths,
        time_grid=time_grid,
        s0=s0,
        mu=mu,
        sigma=sigma,
        horizon_years=horizon_years,
        n_paths=n_paths,
        dt=dt,
        theoretical_mean=theo_mean,
        theoretical_variance=theo_var,
        theoretical_median=theo_median,
    )
