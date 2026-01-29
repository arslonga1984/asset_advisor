"""Tests for input validators."""

import pandas as pd
import pytest

from portfolio_ai.data.validators import (
    validate_dataframe,
    validate_quantity,
    validate_ticker,
    validate_price,
)


class TestValidateTicker:
    def test_valid_us_ticker(self):
        assert validate_ticker("AAPL") == "AAPL"

    def test_valid_us_ticker_single_char(self):
        assert validate_ticker("A") == "A"

    def test_valid_us_ticker_five_chars(self):
        assert validate_ticker("GOOGL") == "GOOGL"

    def test_valid_kr_ticker_ks(self):
        assert validate_ticker("005930.KS") == "005930.KS"

    def test_valid_kr_ticker_kq(self):
        assert validate_ticker("035720.KQ") == "035720.KQ"

    def test_invalid_ticker_empty(self):
        with pytest.raises(ValueError, match="Ticker cannot be empty"):
            validate_ticker("")

    def test_invalid_ticker_too_long(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("TOOLONG")

    def test_invalid_ticker_lowercase(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("aapl")

    def test_invalid_ticker_numbers_only(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("12345")

    def test_invalid_kr_ticker_wrong_suffix(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("005930.XX")

    def test_invalid_kr_ticker_short_code(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("0059.KS")

    def test_ticker_with_spaces_trimmed(self):
        assert validate_ticker("  AAPL  ") == "AAPL"

    def test_valid_index_ticker(self):
        assert validate_ticker("^KS11") == "^KS11"

    def test_valid_spy_etf(self):
        assert validate_ticker("SPY") == "SPY"


class TestValidateQuantity:
    def test_valid_integer_quantity(self):
        assert validate_quantity(10) == 10

    def test_valid_float_quantity(self):
        assert validate_quantity(10.5) == 10.5

    def test_zero_quantity_invalid(self):
        with pytest.raises(ValueError, match="Quantity must be positive"):
            validate_quantity(0)

    def test_negative_quantity_invalid(self):
        with pytest.raises(ValueError, match="Quantity must be positive"):
            validate_quantity(-5)

    def test_string_number_converted(self):
        assert validate_quantity("10") == 10.0

    def test_invalid_string(self):
        with pytest.raises(ValueError, match="Invalid quantity"):
            validate_quantity("abc")


class TestValidatePrice:
    def test_valid_price(self):
        assert validate_price(150.0) == 150.0

    def test_zero_price_invalid(self):
        with pytest.raises(ValueError, match="Price must be positive"):
            validate_price(0)

    def test_negative_price_invalid(self):
        with pytest.raises(ValueError, match="Price must be positive"):
            validate_price(-100.0)

    def test_string_number_converted(self):
        assert validate_price("150.50") == 150.50

    def test_invalid_string(self):
        with pytest.raises(ValueError, match="Invalid price"):
            validate_price("abc")


class TestValidateDataFrame:
    def test_valid_dataframe(self):
        df = pd.DataFrame({
            "ticker": ["AAPL", "GOOGL"],
            "name": ["Apple", "Google"],
            "quantity": [10, 5],
            "avg_cost": [150.0, 2800.0],
        })
        result = validate_dataframe(df)
        assert len(result) == 2

    def test_missing_required_column(self):
        df = pd.DataFrame({
            "ticker": ["AAPL"],
            "name": ["Apple"],
            "quantity": [10],
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_dataframe(df)

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["ticker", "name", "quantity", "avg_cost"])
        with pytest.raises(ValueError, match="DataFrame is empty"):
            validate_dataframe(df)

    def test_optional_currency_column(self):
        df = pd.DataFrame({
            "ticker": ["AAPL"],
            "name": ["Apple"],
            "quantity": [10],
            "avg_cost": [150.0],
            "currency": ["USD"],
        })
        result = validate_dataframe(df)
        assert len(result) == 1

    def test_invalid_ticker_in_dataframe(self):
        df = pd.DataFrame({
            "ticker": ["invalid!!!"],
            "name": ["Bad"],
            "quantity": [10],
            "avg_cost": [100.0],
        })
        with pytest.raises(ValueError, match="Row 1.*Invalid ticker"):
            validate_dataframe(df)

    def test_invalid_quantity_in_dataframe(self):
        df = pd.DataFrame({
            "ticker": ["AAPL"],
            "name": ["Apple"],
            "quantity": [-5],
            "avg_cost": [150.0],
        })
        with pytest.raises(ValueError, match="Row 1.*Quantity must be positive"):
            validate_dataframe(df)

    def test_column_names_case_insensitive(self):
        df = pd.DataFrame({
            "Ticker": ["AAPL"],
            "Name": ["Apple"],
            "Quantity": [10],
            "Avg_Cost": [150.0],
        })
        result = validate_dataframe(df)
        assert len(result) == 1
