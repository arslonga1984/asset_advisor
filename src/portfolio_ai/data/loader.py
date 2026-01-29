"""Portfolio data loader from CSV and Excel files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from portfolio_ai.core.models import Holding, Portfolio
from portfolio_ai.data.validators import validate_dataframe


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with utf-8, falling back to cp949 for Korean data."""
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


def _read_file(path: Path) -> pd.DataFrame:
    """Read a portfolio file (CSV or Excel)."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def load_portfolio(
    path: Path,
    *,
    name: str,
    currency: str,
) -> Portfolio:
    """Load a portfolio from a CSV or Excel file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = _read_file(path)
    validated = validate_dataframe(df)

    has_currency = "currency" in validated.columns
    holdings = tuple(
        Holding(
            ticker=str(row["ticker"]).strip(),
            name=str(row["name"]).strip(),
            quantity=float(row["quantity"]),
            avg_cost=float(row["avg_cost"]),
            currency=str(row["currency"]).strip() if has_currency else currency,
        )
        for _, row in validated.iterrows()
    )

    return Portfolio(
        name=name,
        holdings=holdings,
        currency=currency,
    )
