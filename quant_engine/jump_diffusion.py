"""
Erodha Quantitative Engine: Merton Jump-Diffusion Model
======================================================
Stochastic modeling of asset prices featuring continuous diffusion and discontinuous Poisson jumps.

Model SDE:
    dS_t / S_{t-} = (mu - lambda * kappa) dt + sigma dW_t + (J - 1) dN_t

Where:
    - N_t: Poisson process with jump arrival intensity lambda >= 0.
    - W_t: Standard Brownian motion.
    - J: Multiplicative jump factor. ln(J) ~ N(m_J, delta_J^2).
    - kappa: E[J - 1] = exp(m_J + 0.5 * delta_J^2) - 1 (compensator).
    - mu: Total annualized arithmetic drift.
    - sigma: Annualized continuous diffusion volatility.

Log-Price Evolution:
    d(ln S_t) = (mu - lambda * kappa - 0.5 * sigma^2) dt + sigma dW_t + ln(J) dN_t

Discrete Time-Step Simulation:
    For interval dt:
    1. Jump count: K ~ Poisson(lambda * dt)
    2. Compound jump shock: Sum_{j=1}^K Y_j ~ N(K * m_J, K * delta_J^2)
    3. Continuous shock: (mu - lambda * kappa - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z
    4. S_{t+dt} = S_t * exp( Continuous_Shock + Compound_Jump_Shock )
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass(frozen=True)
class MertonSimulationResult:
    """Container holding simulated paths and theoretical moments for Merton Jump-Diffusion."""
    paths: np.ndarray             # shape: (n_steps + 1, n_paths)
    time_grid: np.ndarray         # shape: (n_steps + 1,)
    s0: float
    mu: float
    sigma: float
    lam: float
    m_j: float
    delta_j: float
    kappa: float
    horizon_years: float
    n_paths: int
    dt: float
    theoretical_mean: float
    total_jumps_simulated: int


def calculate_jump_compensator(m_j: float, delta_j: float) -> float:
    """
    Computes the drift compensator: kappa = E[J - 1] = exp(m_j + 0.5 * delta_j^2) - 1.
    """
    return float(np.exp(m_j + 0.5 * (delta_j ** 2)) - 1.0)


def simulate_merton_paths(
    s0: float,
    mu: float,
    sigma: float,
    lam: float,
    m_j: float,
    delta_j: float,
    horizon_years: float,
    n_steps: int,
    n_paths: int,
    seed: Optional[int] = None,
) -> MertonSimulationResult:
    """
    Simulates exact sample paths for the Merton Jump-Diffusion model.

    Parameters
    ----------
    s0 : float
        Initial asset price (> 0).
    mu : float
        Total annualized expected arithmetic drift.
    sigma : float
        Annualized continuous diffusion volatility (>= 0).
    lam : float
        Annualized Poisson jump intensity lambda (>= 0).
    m_j : float
        Mean of the log-jump size distribution.
    delta_j : float
        Standard deviation of the log-jump size distribution (>= 0).
    horizon_years : float
        Forecast horizon in years (T > 0).
    n_steps : int
        Number of discrete time steps.
    n_paths : int
        Number of Monte Carlo paths.
    seed : Optional[int]
        Random seed for reproducibility.

    Returns
    -------
    MertonSimulationResult
    """
    if s0 <= 0:
        raise ValueError(f"s0 must be positive; got {s0}.")
    if sigma < 0:
        raise ValueError(f"sigma must be non-negative; got {sigma}.")
    if lam < 0:
        raise ValueError(f"lambda must be non-negative; got {lam}.")
    if delta_j < 0:
        raise ValueError(f"delta_j must be non-negative; got {delta_j}.")
    if horizon_years <= 0 or n_steps <= 0 or n_paths <= 0:
        raise ValueError("horizon_years, n_steps, and n_paths must be positive.")

    dt = horizon_years / n_steps
    time_grid = np.linspace(0.0, horizon_years, n_steps + 1)

    # Compute jump compensator
    kappa = calculate_jump_compensator(m_j, delta_j)

    rng = np.random.default_rng(seed)

    # 1. Continuous diffusion shocks
    z = rng.standard_normal(size=(n_steps, n_paths))
    continuous_drift = (mu - lam * kappa - 0.5 * (sigma ** 2)) * dt
    continuous_increments = continuous_drift + sigma * np.sqrt(dt) * z

    # 2. Discontinuous jump shocks
    if lam > 0 and (abs(m_j) > 1e-12 or delta_j > 1e-12):
        # Number of jumps per time step across all paths: Poisson(lam * dt)
        poisson_counts = rng.poisson(lam * dt, size=(n_steps, n_paths))
        total_jumps = int(np.sum(poisson_counts))

        # Vectorized compound jump generation:
        # Sum of K independent N(m_j, delta_j^2) is N(K * m_j, K * delta_j^2)
        # For K = 0, this is identically 0.
        jump_increments = np.zeros((n_steps, n_paths), dtype=np.float64)
        non_zero_mask = poisson_counts > 0

        if np.any(non_zero_mask):
            k_nonzero = poisson_counts[non_zero_mask]
            # Mean = K * m_j, Std = sqrt(K) * delta_j
            jump_means = k_nonzero * m_j
            jump_stds = np.sqrt(k_nonzero) * delta_j
            z_jump = rng.standard_normal(size=len(k_nonzero))
            jump_increments[non_zero_mask] = jump_means + jump_stds * z_jump
    else:
        jump_increments = np.zeros((n_steps, n_paths), dtype=np.float64)
        total_jumps = 0

    # 3. Total log increments and path accumulation
    total_log_increments = continuous_increments + jump_increments
    log_paths = np.vstack([np.zeros((1, n_paths)), np.cumsum(total_log_increments, axis=0)])
    paths = s0 * np.exp(log_paths)

    # Theoretical mean: E[S_T] = S_0 * exp(mu * T)
    theo_mean = s0 * np.exp(mu * horizon_years)

    return MertonSimulationResult(
        paths=paths,
        time_grid=time_grid,
        s0=s0,
        mu=mu,
        sigma=sigma,
        lam=lam,
        m_j=m_j,
        delta_j=delta_j,
        kappa=kappa,
        horizon_years=horizon_years,
        n_paths=n_paths,
        dt=dt,
        theoretical_mean=theo_mean,
        total_jumps_simulated=total_jumps,
    )
