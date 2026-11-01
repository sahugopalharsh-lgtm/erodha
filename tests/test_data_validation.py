"""
Unit tests for quant_engine.data_validation
===========================================
Deterministic validation tests for historical market price series.
"""

import numpy as np
import pandas as pd
import pytest

from quant_engine.data_validation import (
    DataValidationError,
    ValidationResult,
    validate_price_series,
    validate_symbol,
)


def create_sample_price_df(
    n_days: int = 50,
    start_date: str = "2024-01-01",
    start_price: float = 100.0,
    daily_growth: float = 0.001,
    col_name: str = "Adj Close",
) -> pd.DataFrame:
    """Helper to generate clean synthetic price series."""
    dates = pd.date_range(start=start_date, periods=n_days, freq="B")
    prices = start_price * np.exp(daily_growth * np.arange(n_days))
    return pd.DataFrame({col_name: prices}, index=dates)


class TestValidateSymbol:
    """Tests for ticker symbol validation and normalization."""

    def test_valid_symbols(self):
        assert validate_symbol("aapl") == "AAPL"
        assert validate_symbol("RELIANCE.NS") == "RELIANCE.NS"
        assert validate_symbol("^GSPC") == "^GSPC"
        assert validate_symbol("BRK.B") == "BRK.B"
        assert validate_symbol("tcs-eq") == "TCS-EQ"

    def test_empty_or_none_symbol(self):
        assert validate_symbol(None) == "UNKNOWN_TICKER"
        assert validate_symbol("") == "UNKNOWN_TICKER"
        assert validate_symbol("   ") == "UNKNOWN_TICKER"

    def test_invalid_symbols(self):
        with pytest.raises(DataValidationError, match="Invalid ticker symbol"):
            validate_symbol("AAPL; DROP TABLE")
        with pytest.raises(DataValidationError, match="Invalid ticker symbol"):
            validate_symbol("AAPL$")


class TestValidatePriceSeries:
    """Tests for price series data integrity validation."""

    def test_valid_dataframe_adj_close(self):
        df = create_sample_price_df(n_days=60, col_name="Adj Close")
        result = validate_price_series(df, symbol="AAPL")

        assert isinstance(result, ValidationResult)
        assert result.symbol == "AAPL"
        assert result.price_column == "Adj Close"
        assert result.observation_count == 60
        assert result.is_adjusted is True
        assert len(result.warnings) == 0

    def test_unadjusted_close_generates_warning(self):
        df = create_sample_price_df(n_days=40, col_name="Close")
        result = validate_price_series(df, symbol="MSFT")

        assert result.price_column == "Close"
        assert result.is_adjusted is False
        assert any("Unadjusted prices" in w for w in result.warnings)

    def test_out_of_order_dates_are_sorted(self):
        df = create_sample_price_df(n_days=40)
        # Reverse the order
        df_shuffled = df.iloc[::-1].copy()
        assert not df_shuffled.index.is_monotonic_increasing

        result = validate_price_series(df_shuffled, symbol="GOOG")
        assert result.df.index.is_monotonic_increasing
        assert any("automatically sorted" in w for w in result.warnings)

    def test_duplicate_dates_rejected(self):
        df = create_sample_price_df(n_days=35)
        # Duplicate the first date
        dup_row = df.iloc[[0]].copy()
        df_with_dup = pd.concat([dup_row, df])

        with pytest.raises(DataValidationError, match="Found 1 duplicate"):
            validate_price_series(df_with_dup, symbol="TSLA")

    def test_non_positive_price_rejected(self):
        df = create_sample_price_df(n_days=40)
        df.iloc[10, 0] = 0.0

        with pytest.raises(DataValidationError, match="Found 1 non-positive prices"):
            validate_price_series(df, symbol="NVDA")

        df.iloc[10, 0] = -5.0
        with pytest.raises(DataValidationError, match="Found 1 non-positive prices"):
            validate_price_series(df, symbol="NVDA")

    def test_missing_values_rejected(self):
        df = create_sample_price_df(n_days=40)
        df.iloc[5, 0] = np.nan

        with pytest.raises(DataValidationError, match="contains 1 missing"):
            validate_price_series(df, symbol="AMZN")

    def test_infinite_values_rejected(self):
        df = create_sample_price_df(n_days=40)
        df.iloc[5, 0] = np.inf

        with pytest.raises(DataValidationError, match="contains 1 infinite"):
            validate_price_series(df, symbol="META")

    def test_insufficient_observations_rejected(self):
        df = create_sample_price_df(n_days=15)

        with pytest.raises(DataValidationError, match="below minimum required threshold of 30"):
            validate_price_series(df, symbol="NFLX", min_observations=30)

    def test_empty_input_rejected(self):
        empty_df = pd.DataFrame()
        with pytest.raises(DataValidationError, match="Input dataset is empty"):
            validate_price_series(empty_df, symbol="EMPTY")

    def test_series_input_supported(self):
        dates = pd.date_range("2024-01-01", periods=40, freq="B")
        prices = pd.Series(100.0 + np.arange(40), index=dates, name="Adj Close")
        result = validate_price_series(prices, symbol="SPY")
        assert result.observation_count == 40
        assert isinstance(result.df, pd.DataFrame)
