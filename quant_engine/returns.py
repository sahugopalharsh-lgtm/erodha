"""
Erodha Quantitative Engine: Returns & Volatility Module
======================================================
Mathematical formulations for asset returns and distribution moments.

Equations:
1. Simple (Arithmetic) Return:
   R_t = (S_t - S_{t-1}) / S_{t-1} = S_t / S_{t-1} - 1
   - Additive across assets in a portfolio: R_port = sum(w_i * R_i)
   - Non-additive over time.

2. Logarithmic (Continuously Compounded) Return:
   r_t = ln(S_t / S_{t-1}) = ln(S_t) - ln(S_{t-1})
   - Strictly additive over time: r_{0,T} = sum_{t=1}^T r_t = ln(S_T / S_0)
   - Natural state variable for stochastic calculus (Itô diffusion).

3. Daily & Annualized Volatility:
   s_daily = sqrt( 1/(N-1) * sum((r_t - mean(r))^2) )
   sigma_annual = s_daily * sqrt(tau)  [tau = 252 trading days]

4. Relationship Between Drift (mu) and Mean Log Return (mu_log):
   Under Geometric Brownian Motion: dS_t = mu * S_t dt + sigma * S_t dW_t
   By Itô's lemma: d(ln S_t) = (mu - 0.5 * sigma^2) dt + sigma dW_t
   Therefore:
   mu_annual = mu_log_annual + 0.5 * (sigma_annual^2)
   The -0.5 * sigma^2 term is the Itô convexity correction (volatility drag).

5. Higher Moments & Normality Testing:
   - Skewness and excess kurtosis (fat tails).
   - Jarque-Bera test statistic to formally evaluate departure from normality.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class ReturnStatistics:
    """
    Summary statistics of price returns and distribution moments.
    """
    sample_size: int
    trading_days: int
    mean_daily_log_return: float
    annualized_log_return: float
    daily_volatility: float
    annualized_volatility: float
    arithmetic_mean_daily_return: float
    arithmetic_annualized_return: float
    drift_mu: float  # mu = annualized_log_return + 0.5 * annualized_volatility^2
    skewness: float
    excess_kurtosis: float
    jarque_bera_stat: float
    jarque_bera_p_value: float
    is_normal_5pct: bool  # False if p-value < 0.05 (reject Gaussian hypothesis)


@dataclass(frozen=True)
class ReturnsSeries:
    """
    Container for computed simple and logarithmic return series.
    """
    prices: pd.Series
    simple_returns: pd.Series
    log_returns: pd.Series
    stats: ReturnStatistics


def calculate_returns(
    prices: Union[pd.Series, np.ndarray, list],
    trading_days: int = 252,
) -> ReturnsSeries:
    """
    Computes simple and logarithmic return series from a price series.

    Parameters
    ----------
    prices : pd.Series, np.ndarray, or list
        Strictly positive historical price observations.
    trading_days : int
        Number of trading days per year for annualization (default: 252).

    Returns
    -------
    ReturnsSeries
        Object containing clean simple returns, log returns, and distribution statistics.

    Raises
    ------
    ValueError
        If prices contain non-positive values or fewer than 2 valid observations.
    """
    if isinstance(prices, (list, tuple)):
        price_s = pd.Series(prices)
    elif isinstance(prices, np.ndarray):
        price_s = pd.Series(prices)
    elif isinstance(prices, pd.Series):
        price_s = prices.copy()
    else:
        raise ValueError(f"Unsupported prices type: {type(prices).__name__}")

    if len(price_s) < 2:
        raise ValueError(f"At least 2 price observations required to compute returns; got {len(price_s)}.")

    if (price_s <= 0).any():
        raise ValueError("Price series contains non-positive values; log returns are undefined.")

    # Calculate simple returns: R_t = (S_t - S_{t-1}) / S_{t-1}
    simple_returns = price_s.pct_change().dropna()

    # Calculate log returns: r_t = ln(S_t / S_{t-1})
    log_returns = np.log(price_s / price_s.shift(1)).dropna()

    # Calculate statistics
    stat_obj = compute_return_statistics(log_returns, simple_returns, trading_days=trading_days)

    return ReturnsSeries(
        prices=price_s,
        simple_returns=simple_returns,
        log_returns=log_returns,
        stats=stat_obj,
    )


def compute_return_statistics(
    log_returns: Union[pd.Series, np.ndarray],
    simple_returns: Optional[Union[pd.Series, np.ndarray]] = None,
    trading_days: int = 252,
) -> ReturnStatistics:
    """
    Estimates central moments, annualized drift, volatility, and normality diagnostics.

    Parameters
    ----------
    log_returns : pd.Series or np.ndarray
        Continuously compounded returns.
    simple_returns : Optional[pd.Series or np.ndarray]
        Arithmetic returns (if None, derived via exp(r) - 1).
    trading_days : int
        Annualization factor (typically 252 for daily equity data).

    Returns
    -------
    ReturnStatistics
    """
    lr = np.asarray(log_returns, dtype=np.float64)
    lr = lr[~np.isnan(lr)]
    n = len(lr)
    if n < 2:
        raise ValueError(f"At least 2 valid log return observations required; got {n}.")

    if simple_returns is not None:
        sr = np.asarray(simple_returns, dtype=np.float64)
        sr = sr[~np.isnan(sr)]
    else:
        sr = np.expm1(lr)

    # 1. First moment (Sample Mean)
    mean_daily_log = float(np.mean(lr))
    mean_daily_simple = float(np.mean(sr))

    # 2. Second moment (Sample Volatility with Bessel's correction ddof=1)
    daily_vol = float(np.std(lr, ddof=1))

    # 3. Annualization
    ann_log_return = mean_daily_log * trading_days
    ann_vol = daily_vol * np.sqrt(trading_days)
    ann_simple_return = mean_daily_simple * trading_days

    # 4. Stochastic Drift Parameter mu
    # Under dS = mu * S dt + sigma * S dW, E[ln(S_t/S_0)] = (mu - 0.5*sigma^2)*t
    drift_mu = ann_log_return + 0.5 * (ann_vol ** 2)

    # 5. Higher Moments (Sample Skewness & Excess Kurtosis)
    # If n < 4, higher sample moments have insufficient degrees of freedom
    if n >= 4:
        skew_val = float(stats.skew(lr, bias=False))
        kurt_val = float(stats.kurtosis(lr, fisher=True, bias=False))
        jb_res = stats.jarque_bera(lr)
        jb_stat = float(jb_res.statistic)
        jb_p_val = float(jb_res.pvalue)
    else:
        skew_val = 0.0
        kurt_val = 0.0
        jb_stat = 0.0
        jb_p_val = 1.0

    is_normal_5pct = bool(jb_p_val >= 0.05)

    return ReturnStatistics(
        sample_size=n,
        trading_days=trading_days,
        mean_daily_log_return=mean_daily_log,
        annualized_log_return=ann_log_return,
        daily_volatility=daily_vol,
        annualized_volatility=ann_vol,
        arithmetic_mean_daily_return=mean_daily_simple,
        arithmetic_annualized_return=ann_simple_return,
        drift_mu=drift_mu,
        skewness=skew_val,
        excess_kurtosis=kurt_val,
        jarque_bera_stat=jb_stat,
        jarque_bera_p_value=jb_p_val,
        is_normal_5pct=is_normal_5pct,
    )


def chronological_train_test_split(
    data: Union[pd.DataFrame, pd.Series],
    split_point: Union[float, str, pd.Timestamp] = 0.8,
) -> Tuple[Union[pd.DataFrame, pd.Series], Union[pd.DataFrame, pd.Series]]:
    """
    Splits time series data chronologically to guarantee zero data leakage.

    Parameters
    ----------
    data : pd.DataFrame or pd.Series
        Time series indexed monotonically by DatetimeIndex or integer sequence.
    split_point : float, str, or pd.Timestamp
        If float between 0 and 1: fraction of initial observations for training (e.g., 0.8).
        If str or pd.Timestamp: explicit cutoff date (train <= cutoff, test > cutoff).

    Returns
    -------
    Tuple[train_data, test_data]
        Strictly partitioned subsets.

    Raises
    ------
    ValueError
        If split_point is invalid or leaves either partition empty.
    """
    n = len(data)
    if n < 2:
        raise ValueError(f"Cannot split dataset with {n} observations.")

    if isinstance(split_point, (float, int)) and 0.0 < split_point < 1.0:
        split_idx = int(np.floor(n * split_point))
        if split_idx == 0 or split_idx >= n:
            raise ValueError(f"Split fraction {split_point} produces an empty train or test partition.")
        train = data.iloc[:split_idx]
        test = data.iloc[split_idx:]
    elif isinstance(split_point, (str, pd.Timestamp)):
        cutoff = pd.Timestamp(split_point)
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have a DatetimeIndex to split on a date cutoff.")
        train = data.loc[data.index <= cutoff]
        test = data.loc[data.index > cutoff]
        if train.empty or test.empty:
            raise ValueError(
                f"Cutoff date '{cutoff}' results in empty train (size={len(train)}) "
                f"or test (size={len(test)}) partition."
            )
    else:
        raise ValueError(
            f"Invalid split_point '{split_point}'. Must be a float in (0, 1) or a valid date."
        )

    return train, test
