"""Input validation for portfolio data."""

from __future__ import annotations

import re

import pandas as pd

US_TICKER_PATTERN = re.compile(r"^[A-Z]{1,5}$")
KR_TICKER_PATTERN = re.compile(r"^\d{6}\.(KS|KQ)$")
INDEX_TICKER_PATTERN = re.compile(r"^\^[A-Z0-9]+$")

REQUIRED_COLUMNS = {"ticker", "name", "quantity", "avg_cost"}


def validate_ticker(ticker: str) -> str:
    """Validate and normalize a ticker symbol."""
    ticker = ticker.strip()
    if not ticker:
        raise ValueError("Ticker cannot be empty")

    if (
        US_TICKER_PATTERN.match(ticker)
        or KR_TICKER_PATTERN.match(ticker)
        or INDEX_TICKER_PATTERN.match(ticker)
    ):
        return ticker

    raise ValueError(f"Invalid ticker: '{ticker}'")


def validate_quantity(quantity: float | int | str) -> float:
    """Validate that quantity is a positive number."""
    try:
        value = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity: '{quantity}'")

    if value <= 0:
        raise ValueError("Quantity must be positive")
    return value


def validate_price(price: float | int | str) -> float:
    """Validate that price is a positive number."""
    try:
        value = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price: '{price}'")

    if value <= 0:
        raise ValueError("Price must be positive")
    return value


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate a DataFrame containing portfolio holdings."""
    normalized = df.copy()
    normalized.columns = [c.lower().strip() for c in normalized.columns]

    missing = REQUIRED_COLUMNS - set(normalized.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    if normalized.empty:
        raise ValueError("DataFrame is empty")

    errors: list[str] = []
    for idx, row in normalized.iterrows():
        row_num = idx + 1 if isinstance(idx, int) else idx
        try:
            validate_ticker(str(row["ticker"]))
        except ValueError as e:
            errors.append(f"Row {row_num}: {e}")
        try:
            validate_quantity(row["quantity"])
        except ValueError as e:
            errors.append(f"Row {row_num}: {e}")
        try:
            validate_price(row["avg_cost"])
        except ValueError as e:
            errors.append(f"Row {row_num}: {e}")

    if errors:
        raise ValueError("\n".join(errors))

    return normalized
