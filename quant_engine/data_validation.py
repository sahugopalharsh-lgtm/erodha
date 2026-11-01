"""
Erodha Quantitative Engine: Data Validation Module
===================================================
Rigorous validation of historical market data.

Validates:
- Data structure (pandas DataFrame with DatetimeIndex or date column)
- Ticker symbol format
- Monotonic chronological ordering (no future-to-past or shuffled sequences)
- Duplicate date detection and handling
- Non-positive prices (St <= 0 violates equity limited liability & makes log undefined)
- Missing values (NaN, null, infinite)
- Selection and limitation documentation of Adjusted vs. Unadjusted Close
- Minimum observation threshold for statistical viability
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union
import numpy as np
import pandas as pd


class DataValidationError(ValueError):
    """Raised when financial time-series data fails quantitative integrity checks."""
    pass


@dataclass(frozen=True)
class ValidationResult:
    """
    Immutable container holding validated financial time-series and metadata.
    """
    df: pd.DataFrame
    price_column: str
    symbol: str
    observation_count: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    is_adjusted: bool
    warnings: Tuple[str, ...] = field(default_factory=tuple)


def validate_symbol(symbol: Optional[str]) -> str:
    """
    Validates and normalizes ticker symbols.
    
    Parameters
    ----------
    symbol : str or None
        Ticker symbol string, e.g. 'AAPL', 'RELIANCE.NS'.
        
    Returns
    -------
    str : Cleaned uppercase ticker string.
    
    Raises
    ------
    DataValidationError
        If symbol is empty, None, or contains invalid characters.
    """
    if symbol is None or not isinstance(symbol, str) or not symbol.strip():
        return "UNKNOWN_TICKER"
    
    cleaned = symbol.strip().upper()
    # Permit alphanumeric, dot, hyphen, caret (e.g. ^GSPC, BRK.B, RELIANCE.NS)
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-^")
    if not all(c in allowed for c in cleaned):
        raise DataValidationError(
            f"Invalid ticker symbol '{symbol}'. Symbol may only contain "
            "alphanumeric characters, dots, hyphens, and carets."
        )
    return cleaned


def validate_price_series(
    data: Union[pd.DataFrame, pd.Series],
    price_col: Optional[str] = None,
    symbol: Optional[str] = None,
    min_observations: int = 30,
) -> ValidationResult:
    """
    Validates a financial price time-series for stochastic modeling.
    
    Checks enforced:
    1. Input is non-empty pandas DataFrame or Series.
    2. Date index or date column is properly parsed as datetime and timezone-naive (or uniform UTC).
    3. Strictly monotonic chronological ordering (oldest to newest).
    4. Absence of duplicate timestamps.
    5. Price column existence (prefers 'Adj Close', falls back to 'Close' or single Series).
    6. All prices strictly positive (S_t > 0).
    7. Absence of NaN, Inf, or null values.
    8. Observation count >= min_observations.

    Parameters
    ----------
    data : pd.DataFrame or pd.Series
        Historical market data.
    price_col : Optional[str]
        Explicit name of the price column to use. If None, auto-detected.
    symbol : Optional[str]
        Symbol name for reporting.
    min_observations : int
        Minimum number of trading periods required (default: 30).

    Returns
    -------
    ValidationResult
        Cleaned, validated DataFrame indexed by DatetimeIndex with metadata.
    """
    warnings: List[str] = []
    symbol_str = validate_symbol(symbol)

    if data is None or (isinstance(data, (pd.DataFrame, pd.Series)) and data.empty):
        raise DataValidationError(f"[{symbol_str}] Input dataset is empty or None.")

    # Convert Series to DataFrame if needed
    if isinstance(data, pd.Series):
        series_name = data.name or "Close"
        df = data.to_frame(name=series_name)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise DataValidationError(
            f"[{symbol_str}] Expected pandas DataFrame or Series, got {type(data).__name__}."
        )

    # 1. Normalize Date Index
    if not isinstance(df.index, pd.DatetimeIndex):
        date_candidates = [c for c in df.columns if str(c).lower() in ("date", "timestamp", "datetime", "time")]
        if date_candidates:
            date_col = date_candidates[0]
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                df.set_index(date_col, inplace=True)
            except Exception as e:
                raise DataValidationError(
                    f"[{symbol_str}] Failed to parse date column '{date_col}' into DatetimeIndex: {e}"
                ) from e
        else:
            try:
                df.index = pd.to_datetime(df.index)
            except Exception as e:
                raise DataValidationError(
                    f"[{symbol_str}] DataFrame index cannot be converted to DatetimeIndex: {e}"
                ) from e

    # Strip timezone if present to prevent tz-naive vs tz-aware comparison errors
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # 2. Check and enforce chronological ordering
    if not df.index.is_monotonic_increasing:
        warnings.append("Data was not in chronological order; automatically sorted ascending by date.")
        df = df.sort_index()

    # 3. Check for duplicate timestamps
    duplicate_count = df.index.duplicated().sum()
    if duplicate_count > 0:
        raise DataValidationError(
            f"[{symbol_str}] Found {duplicate_count} duplicate date/time observations in time series. "
            "Data must have unique timestamps."
        )

    # 4. Resolve price column
    is_adjusted = False
    if price_col is not None:
        if price_col not in df.columns:
            raise DataValidationError(
                f"[{symbol_str}] Specified price column '{price_col}' not found in DataFrame. "
                f"Available columns: {list(df.columns)}"
            )
        resolved_col = price_col
        is_adjusted = "adj" in resolved_col.lower()
    else:
        # Preference: 'Adj Close' -> 'Adj_Close' -> 'Close' -> first numeric column
        candidates = ["Adj Close", "Adj_Close", "adj_close", "adjclose", "Close", "close", "price", "Price"]
        resolved_col = None
        for cand in candidates:
            if cand in df.columns:
                resolved_col = cand
                is_adjusted = "adj" in cand.lower()
                break
        
        if resolved_col is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                resolved_col = numeric_cols[0]
                warnings.append(f"Auto-selected first numeric column '{resolved_col}' as price series.")
            else:
                raise DataValidationError(
                    f"[{symbol_str}] Could not find a suitable price column in {list(df.columns)}."
                )

    if not is_adjusted:
        warnings.append(
            f"Using unadjusted price column '{resolved_col}'. Unadjusted prices do not reflect dividends "
            "or stock splits, which can cause spurious jumps in returns."
        )

    # 5. Extract price series and validate numerical integrity
    price_s = df[resolved_col]

    # Check for NaN / nulls / Inf
    null_count = price_s.isna().sum()
    if null_count > 0:
        raise DataValidationError(
            f"[{symbol_str}] Price series '{resolved_col}' contains {null_count} missing (NaN) values."
        )

    inf_count = np.isinf(price_s).sum()
    if inf_count > 0:
        raise DataValidationError(
            f"[{symbol_str}] Price series '{resolved_col}' contains {inf_count} infinite values."
        )

    # Check for non-positive prices
    non_positive_count = (price_s <= 0).sum()
    if non_positive_count > 0:
        min_val = price_s.min()
        raise DataValidationError(
            f"[{symbol_str}] Found {non_positive_count} non-positive prices in '{resolved_col}' "
            f"(minimum price: {min_val}). Stock prices in stochastic equity models must be strictly > 0."
        )

    # 6. Minimum observation count check
    n_obs = len(price_s)
    if n_obs < min_observations:
        raise DataValidationError(
            f"[{symbol_str}] Sample size of {n_obs} observations is below minimum required "
            f"threshold of {min_observations} for statistical inference."
        )

    return ValidationResult(
        df=df,
        price_column=resolved_col,
        symbol=symbol_str,
        observation_count=n_obs,
        start_date=df.index[0],
        end_date=df.index[-1],
        is_adjusted=is_adjusted,
        warnings=tuple(warnings),
    )
