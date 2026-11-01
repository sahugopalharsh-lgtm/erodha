"""
Erodha Quantitative Engine: Model Evaluation & Backtesting Module
=================================================================
Statistical verification of predictive distributions and VaR exceedance backtesting.

Metrics:
1. Point Prediction Error:
   - Mean Absolute Error (MAE): (1/N) * sum |S_t - S_hat_median|
   - Root Mean Squared Error (RMSE): sqrt( (1/N) * sum (S_t - S_hat_median)^2 )

2. Empirical Coverage of Predictive Quantiles:
   - 90% Forecast Envelope: Empirical fraction of actual prices in [q_05, q_95] (nominal = 0.90)
   - 50% Interquartile Envelope: Empirical fraction in [q_25, q_75] (nominal = 0.50)

3. Value at Risk Backtesting (Kupiec Proportion of Failures Test):
   H0: True exception probability is p = (1 - alpha)
   Likelihood Ratio Statistic:
       LR_POF = -2 * ln[ ( (1 - p)^(N - x) * p^x ) / ( (1 - x/N)^(N - x) * (x/N)^x ) ]
   Under H0, LR_POF ~ Chi-Square(df = 1).
   p_value = 1 - Chi2_CDF(LR_POF, df = 1).
   If p_value < 0.05, H0 is rejected.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats

from quant_engine.returns import ReturnsSeries, calculate_returns, chronological_train_test_split
from quant_engine.estimation import estimate_model_parameters
from quant_engine.monte_carlo import run_monte_carlo_forecast


@dataclass(frozen=True)
class KupiecTestResult:
    """Results from the Kupiec Proportion of Failures (POF) Likelihood Ratio test."""
    total_observations: int
    failures: int
    failure_rate: float
    expected_failure_rate: float
    likelihood_ratio_stat: float
    p_value: float
    is_accepted_5pct: bool


@dataclass(frozen=True)
class BacktestEvaluationResult:
    """Out-of-sample forecast and risk backtest results."""
    symbol: str
    train_size: int
    test_size: int
    mae_gbm: float
    rmse_gbm: float
    coverage_90_gbm: float
    mae_merton: float
    rmse_merton: float
    coverage_90_merton: float
    kupiec_var_95: KupiecTestResult
    best_point_model: str
    best_distribution_model: str


def kupiec_pof_test(
    failures: int,
    total_obs: int,
    confidence_level: float = 0.95,
) -> KupiecTestResult:
    """
    Performs Kupiec's POF likelihood ratio test on VaR violations.
    """
    p = 1.0 - confidence_level
    n = total_obs
    x = failures
    hat_p = x / n if n > 0 else 0.0

    if x == 0:
        # Limit as x -> 0: (hat_p)^x = 1, (1 - hat_p)^(n-x) = 1
        lr = -2.0 * np.log(((1.0 - p) ** n))
    elif x == n:
        lr = -2.0 * np.log((p ** n))
    else:
        # Standard likelihood ratio
        num = ((1.0 - p) ** (n - x)) * (p ** x)
        denom = ((1.0 - hat_p) ** (n - x)) * (hat_p ** x)
        lr = -2.0 * np.log(max(1e-300, num / denom))

    # Degrees of freedom = 1
    p_val = float(1.0 - stats.chi2.cdf(lr, df=1))
    accepted = bool(p_val >= 0.05)

    return KupiecTestResult(
        total_observations=n,
        failures=x,
        failure_rate=hat_p,
        expected_failure_rate=p,
        likelihood_ratio_stat=float(lr),
        p_value=p_val,
        is_accepted_5pct=accepted,
    )


def evaluate_forecast_models(
    price_series: pd.Series,
    symbol: str = "ASSET",
    split_ratio: float = 0.8,
    n_paths: int = 2000,
    seed: int = 42,
) -> BacktestEvaluationResult:
    """
    Performs rigorous chronological backtesting comparing GBM and Merton models.
    """
    train_prices, test_prices = chronological_train_test_split(price_series, split_point=split_ratio)
    
    # 1. Calibrate models exclusively on training data (Zero data leakage)
    params = estimate_model_parameters(train_prices.values, symbol=symbol)
    s0 = float(train_prices.iloc[-1])
    test_actual = test_prices.values
    horizon = len(test_actual)

    # 2. Simulate GBM out-of-sample
    fc_gbm = run_monte_carlo_forecast(
        model="GBM",
        s0=s0,
        mu=params.mu_gbm,
        sigma=params.sigma_gbm,
        horizon_days=horizon,
        n_steps=horizon,
        n_paths=n_paths,
        seed=seed,
    )

    # 3. Simulate Merton out-of-sample
    fc_merton = run_monte_carlo_forecast(
        model="MERTON",
        s0=s0,
        mu=params.mu_merton,
        sigma=params.sigma_continuous,
        lam=params.lam,
        m_j=params.m_j,
        delta_j=params.delta_j,
        horizon_days=horizon,
        n_steps=horizon,
        n_paths=n_paths,
        seed=seed,
    )

    # 4. Point evaluation: MAE and RMSE against median forecast path
    # Exclude t=0 which is s0
    pred_gbm = fc_gbm.median_path[1:]
    pred_merton = fc_merton.median_path[1:]

    mae_gbm = float(np.mean(np.abs(test_actual - pred_gbm)))
    rmse_gbm = float(np.sqrt(np.mean((test_actual - pred_gbm) ** 2)))

    mae_merton = float(np.mean(np.abs(test_actual - pred_merton)))
    rmse_merton = float(np.sqrt(np.mean((test_actual - pred_merton) ** 2)))

    # 5. Distribution evaluation: 90% quantile envelope coverage [q05, q95]
    cov_gbm = float(np.mean(
        (test_actual >= fc_gbm.q05_path[1:]) & (test_actual <= fc_gbm.q95_path[1:])
    ))
    cov_merton = float(np.mean(
        (test_actual >= fc_merton.q05_path[1:]) & (test_actual <= fc_merton.q95_path[1:])
    ))

    # 6. VaR 95% Backtest on historical test returns
    test_ret = np.diff(np.log(test_actual))
    train_ret = np.diff(np.log(train_prices.values))
    var_95_threshold = -float(np.percentile(train_ret, 5))
    violations = int(np.sum(-test_ret > var_95_threshold))
    kupiec_res = kupiec_pof_test(violations, len(test_ret), confidence_level=0.95)

    best_point = "MERTON" if mae_merton < mae_gbm else "GBM"
    # Closer to 0.90 nominal coverage wins distribution test
    best_dist = "MERTON" if abs(cov_merton - 0.90) <= abs(cov_gbm - 0.90) else "GBM"

    return BacktestEvaluationResult(
        symbol=symbol,
        train_size=len(train_prices),
        test_size=len(test_prices),
        mae_gbm=mae_gbm,
        rmse_gbm=rmse_gbm,
        coverage_90_gbm=cov_gbm,
        mae_merton=mae_merton,
        rmse_merton=rmse_merton,
        coverage_90_merton=cov_merton,
        kupiec_var_95=kupiec_res,
        best_point_model=best_point,
        best_distribution_model=best_dist,
    )
