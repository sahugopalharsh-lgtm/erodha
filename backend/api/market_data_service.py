"""
Market Data Service for Erodha Backend
======================================
Retrieves and validates equity time series from Yahoo Finance (with synthetic fallback).
"""

import os
import zlib
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
import yfinance as yf

from quant_engine.data_validation import validate_price_series, ValidationResult
from quant_engine.returns import calculate_returns, ReturnsSeries


def fetch_historical_prices(
    symbol: str = "AAPL",
    period: str = "1y",
) -> Tuple[pd.Series, ReturnsSeries, ValidationResult, bool]:
    """
    Retrieves historical price series, validates integrity, and computes returns.

    Returns
    -------
    Tuple[prices_series, returns_series, validation_result, is_synthetic_flag]
    """
    clean_sym = symbol.strip().upper()
    is_synthetic = False

    try:
        ticker = yf.Ticker(clean_sym)
        df = ticker.history(period=period)
        if df.empty or len(df) < 20:
            raise ValueError(f"Insufficient observations returned by yfinance for '{clean_sym}'.")
        
        # Prefer 'Adj Close', fallback to 'Close'
        if "Adj Close" not in df.columns and "Close" in df.columns:
            df["Adj Close"] = df["Close"]

        val_res = validate_price_series(df, symbol=clean_sym)
        price_series = val_res.df[val_res.price_column]
    except Exception as exc:
        # Real data is the default. Synthetic data is only allowed for offline demos,
        # and only when explicitly enabled: ERODHA_ALLOW_SYNTHETIC=1
        if os.environ.get("ERODHA_ALLOW_SYNTHETIC", "0") != "1":
            raise RuntimeError(
                f"Could not fetch market data for '{clean_sym}' ({exc}). "
                "Check the ticker (Indian stocks need a suffix, e.g. RELIANCE.NS or TCS.BO) "
                "and your internet connection."
            ) from exc
        is_synthetic = True
        n_days = 252 if period in ("1y", "max") else (60 if period in ("3mo", "1mo") else 500)
        last_bday = pd.offsets.BDay().rollback(pd.Timestamp.now().normalize())  # weekend-safe
        dates = pd.bdate_range(end=last_bday, periods=n_days)
        
        # Synthetic parameters based on typical equity: mu=10%, sigma=22%
        dt = 1.0 / 252.0
        rng = np.random.default_rng(zlib.crc32(clean_sym.encode()))
        log_increments = (0.10 - 0.5 * 0.22**2) * dt + 0.22 * np.sqrt(dt) * rng.standard_normal(n_days)
        prices = 150.0 * np.exp(np.cumsum(log_increments))
        
        df = pd.DataFrame({"Adj Close": prices}, index=dates)
        val_res = validate_price_series(df, symbol=clean_sym)
        price_series = val_res.df[val_res.price_column]

    ret_series = calculate_returns(price_series)
    return price_series, ret_series, val_res, is_synthetic
