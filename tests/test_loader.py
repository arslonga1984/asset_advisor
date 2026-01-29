"""Tests for data loader."""

from pathlib import Path

import pandas as pd
import pytest

from portfolio_ai.core.models import Portfolio
from portfolio_ai.data.loader import load_portfolio


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample CSV file."""
    csv_content = "ticker,name,quantity,avg_cost\nAAPL,Apple Inc.,10,150.0\nGOOGL,Alphabet Inc.,5,2800.0\n"
    path = tmp_path / "portfolio.csv"
    path.write_text(csv_content, encoding="utf-8")
    return path


@pytest.fixture
def sample_csv_with_currency(tmp_path: Path) -> Path:
    csv_content = "ticker,name,quantity,avg_cost,currency\nAAPL,Apple Inc.,10,150.0,USD\n005930.KS,삼성전자,100,70000.0,KRW\n"
    path = tmp_path / "portfolio.csv"
    path.write_text(csv_content, encoding="utf-8")
    return path


@pytest.fixture
def sample_excel(tmp_path: Path) -> Path:
    """Create a sample Excel file."""
    df = pd.DataFrame({
        "ticker": ["AAPL", "GOOGL"],
        "name": ["Apple Inc.", "Alphabet Inc."],
        "quantity": [10, 5],
        "avg_cost": [150.0, 2800.0],
    })
    path = tmp_path / "portfolio.xlsx"
    df.to_excel(path, index=False)
    return path


@pytest.fixture
def sample_csv_cp949(tmp_path: Path) -> Path:
    """Create a CP949-encoded CSV for Korean data."""
    csv_content = "ticker,name,quantity,avg_cost\n005930.KS,삼성전자,100,70000.0\n035720.KQ,카카오,50,55000.0\n"
    path = tmp_path / "portfolio_kr.csv"
    path.write_text(csv_content, encoding="cp949")
    return path


class TestLoadPortfolio:
    def test_load_csv(self, sample_csv: Path):
        portfolio = load_portfolio(sample_csv, name="Test", currency="USD")
        assert isinstance(portfolio, Portfolio)
        assert portfolio.name == "Test"
        assert len(portfolio.holdings) == 2
        assert portfolio.holdings[0].ticker == "AAPL"
        assert portfolio.holdings[1].ticker == "GOOGL"

    def test_load_excel(self, sample_excel: Path):
        portfolio = load_portfolio(sample_excel, name="Excel Test", currency="USD")
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.holdings) == 2

    def test_load_csv_cp949_fallback(self, sample_csv_cp949: Path):
        portfolio = load_portfolio(sample_csv_cp949, name="KR Test", currency="KRW")
        assert len(portfolio.holdings) == 2
        assert portfolio.holdings[0].name == "삼성전자"

    def test_load_portfolio_quantities(self, sample_csv: Path):
        portfolio = load_portfolio(sample_csv, name="Test", currency="USD")
        assert portfolio.holdings[0].quantity == 10
        assert portfolio.holdings[0].avg_cost == 150.0

    def test_load_portfolio_currency(self, sample_csv: Path):
        portfolio = load_portfolio(sample_csv, name="Test", currency="USD")
        assert portfolio.currency == "USD"
        assert portfolio.holdings[0].currency == "USD"

    def test_load_portfolio_with_mixed_currency(self, sample_csv_with_currency: Path):
        portfolio = load_portfolio(
            sample_csv_with_currency, name="Mixed", currency="USD"
        )
        assert portfolio.holdings[0].currency == "USD"
        assert portfolio.holdings[1].currency == "KRW"

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_portfolio(Path("nonexistent.csv"), name="Test", currency="USD")

    def test_load_unsupported_format(self, tmp_path: Path):
        path = tmp_path / "portfolio.json"
        path.write_text("{}")
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_portfolio(path, name="Test", currency="USD")
