"""
Erodha Quantitative Engine: Financial Risk Assessment Module
============================================================
Mathematical formulation and estimation of Value at Risk (VaR),
Expected Shortfall (ES / CVaR), and Maximum Drawdown.

Definitions:
1. Portfolio Value & Loss Definition:
   Let V_0 be initial position value.
   Terminal value: V_T = V_0 * (S_T / S_0)
   Arithmetic return: R = (S_T - S_0) / S_0
   Loss: L = -(V_T - V_0) = -V_0 * R
   Percentage Loss: L_% = -R

2. Value at Risk (VaR_alpha):
   VaR_alpha = inf{ l : P(L <= l) >= alpha }
   At confidence level alpha (e.g. 0.95 or 0.99):
   - VaR is expressed as a POSITIVE dollar loss amount or positive percentage loss.
   - For empirical returns, VaR_% is -quantile(R, 1 - alpha).

3. Expected Shortfall (ES_alpha / Conditional VaR):
   The expected loss given that the loss exceeds VaR_alpha:
   ES_alpha = E[ L | L >= VaR_alpha ]
   Empirical estimator: mean of losses in the worst (1 - alpha) tail fraction.

4. Parametric (Gaussian) Estimators:
   VaR_{alpha, param} = -mu + sigma * z_alpha
   where z_alpha = Phi^{-1}(alpha) (e.g., 1.645 for 95%, 2.326 for 99%)
   ES_{alpha, param} = -mu + sigma * [ phi(z_alpha) / (1 - alpha) ]

5. Maximum Drawdown (MDD):
   MDD = max_{t} [ (Peak_t - S_t) / Peak_t ] where Peak_t = max_{s <= t} S_s
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class RiskMetrics:
    """Standardized container for financial tail risk metrics."""
    confidence_level: float        # e.g., 0.95 or 0.99
    horizon_days: int              # e.g., 1 day or 252 days
    portfolio_value: float         # Currency value (V_0)
    
    # Value at Risk (VaR)
    var_percentage: float          # Positive fraction (e.g., 0.05 = 5% loss)
    var_amount: float              # Positive currency amount (e.g., $5,000)
    
    # Expected Shortfall (ES / CVaR)
    es_percentage: float           # Positive fraction (e.g., 0.075 = 7.5% loss)
    es_amount: float               # Positive currency amount
    
    # Method tag
    method: str                    # 'HISTORICAL', 'PARAMETRIC', or 'MONTE_CARLO'


@dataclass(frozen=True)
class RiskReport:
    """Comprehensive risk summary across multiple confidence levels."""
    portfolio_value: float
    horizon_days: int
    var_95: RiskMetrics
    var_99: RiskMetrics
    max_drawdown_percentage: float
    loss_distribution: np.ndarray  # Sample of percentage losses (positive = loss)


def compute_empirical_var_es(
    returns: Union[np.ndarray, pd.Series],
    confidence_level: float = 0.95,
    portfolio_value: float = 100_000.0,
    horizon_days: int = 1,
    method_name: str = "HISTORICAL",
) -> RiskMetrics:
    """
    Computes empirical VaR and Expected Shortfall from a sample of returns.

    Parameters
    ----------
    returns : np.ndarray or pd.Series
        Arithmetic returns over the specified horizon.
    confidence_level : float
        Confidence level, e.g. 0.95 or 0.99 (0 < alpha < 1).
    portfolio_value : float
        Initial position value V_0.
    horizon_days : int
        Holding period in days.
    method_name : str
        Label for reporting ('HISTORICAL' or 'MONTE_CARLO').

    Returns
    -------
    RiskMetrics
    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError(f"Confidence level must be strictly between 0 and 1; got {confidence_level}.")
    if portfolio_value <= 0:
        raise ValueError(f"Portfolio value must be positive; got {portfolio_value}.")

    r = np.asarray(returns, dtype=np.float64)
    r = r[~np.isnan(r)]
    if len(r) < 10:
        raise ValueError(f"At least 10 return observations required for risk assessment; got {len(r)}.")

    # Percentage loss: L_% = -R
    losses = -r

    # VaR_alpha is the alpha-quantile of the loss distribution
    # (consistent with (1 - alpha) quantile of returns)
    var_pct = float(np.percentile(losses, confidence_level * 100))
    var_amt = float(portfolio_value * var_pct)

    # Expected Shortfall: mean loss given loss >= VaR
    tail_losses = losses[losses >= var_pct]
    if len(tail_losses) > 0:
        es_pct = float(np.mean(tail_losses))
    else:
        es_pct = var_pct

    es_amt = float(portfolio_value * es_pct)

    return RiskMetrics(
        confidence_level=confidence_level,
        horizon_days=horizon_days,
        portfolio_value=portfolio_value,
        var_percentage=var_pct,
        var_amount=var_amt,
        es_percentage=es_pct,
        es_amount=es_amt,
        method=method_name,
    )


def compute_parametric_var_es(
    mean_return: float,
    volatility: float,
    confidence_level: float = 0.95,
    portfolio_value: float = 100_000.0,
    horizon_days: int = 1,
) -> RiskMetrics:
    """
    Computes Gaussian parametric VaR and Expected Shortfall.
    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")
    if volatility < 0:
        raise ValueError("Volatility cannot be negative.")

    z_alpha = stats.norm.ppf(confidence_level)
    # VaR = -(mu + sigma * (-z_alpha)) = -mu + sigma * z_alpha
    var_pct = float(-mean_return + volatility * z_alpha)
    var_amt = float(portfolio_value * var_pct)

    # ES = -mu + sigma * (phi(z_alpha) / (1 - alpha))
    phi_z = stats.norm.pdf(z_alpha)
    es_pct = float(-mean_return + volatility * (phi_z / (1.0 - confidence_level)))
    es_amt = float(portfolio_value * es_pct)

    return RiskMetrics(
        confidence_level=confidence_level,
        horizon_days=horizon_days,
        portfolio_value=portfolio_value,
        var_percentage=var_pct,
        var_amount=var_amt,
        es_percentage=es_pct,
        es_amount=es_amt,
        method="PARAMETRIC",
    )


def calculate_maximum_drawdown(prices: Union[np.ndarray, pd.Series]) -> float:
    """
    Computes the maximum peak-to-trough decline as a positive percentage.
    """
    p = np.asarray(prices, dtype=np.float64)
    if len(p) < 2:
        return 0.0
    running_max = np.maximum.accumulate(p)
    drawdowns = (running_max - p) / running_max
    return float(np.max(drawdowns))


def generate_risk_report(
    returns: Union[np.ndarray, pd.Series],
    prices: Optional[Union[np.ndarray, pd.Series]] = None,
    portfolio_value: float = 100_000.0,
    horizon_days: int = 1,
    method: str = "HISTORICAL",
) -> RiskReport:
    """
    Generates a consolidated risk assessment report at 95% and 99% confidence.
    """
    var_95 = compute_empirical_var_es(
        returns=returns,
        confidence_level=0.95,
        portfolio_value=portfolio_value,
        horizon_days=horizon_days,
        method_name=method,
    )
    var_99 = compute_empirical_var_es(
        returns=returns,
        confidence_level=0.99,
        portfolio_value=portfolio_value,
        horizon_days=horizon_days,
        method_name=method,
    )

    if prices is not None:
        mdd = calculate_maximum_drawdown(prices)
    else:
        mdd = 0.0

    r = np.asarray(returns, dtype=np.float64)
    losses = -r[~np.isnan(r)]

    return RiskReport(
        portfolio_value=portfolio_value,
        horizon_days=horizon_days,
        var_95=var_95,
        var_99=var_99,
        max_drawdown_percentage=mdd,
        loss_distribution=losses,
    )


def horizon_returns_from_daily(daily_returns, horizon_days: int) -> np.ndarray:
    """Overlapping h-day compounded simple returns from daily simple returns.

    VaR/ES for a multi-day holding period must be computed on multi-day returns,
    not on 1-day returns relabelled with a different horizon.
    """
    r = np.asarray(daily_returns, dtype=np.float64)
    r = r[~np.isnan(r)]
    if horizon_days <= 1:
        return r
    if len(r) < horizon_days + 30:
        raise ValueError(
            f"Need at least {horizon_days + 30} daily observations for a {horizon_days}-day "
            f"horizon; got {len(r)}. Use a longer history window."
        )
    growth = np.cumprod(1.0 + r)
    growth = np.concatenate([[1.0], growth])
    return growth[horizon_days:] / growth[:-horizon_days] - 1.0
