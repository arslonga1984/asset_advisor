"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from click.testing import CliRunner

from portfolio_ai.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    csv_content = "ticker,name,quantity,avg_cost\nAAPL,Apple Inc.,10,150.0\nMSFT,Microsoft Corp.,5,300.0\n"
    path = tmp_path / "portfolio.csv"
    path.write_text(csv_content, encoding="utf-8")
    return path


@pytest.fixture
def mock_market():
    provider = MagicMock()
    provider.get_current_price.side_effect = lambda t: {
        "AAPL": 175.0,
        "MSFT": 350.0,
        "SPY": 450.0,
    }.get(t)
    provider.get_sector.side_effect = lambda t: {
        "AAPL": "Technology",
        "MSFT": "Technology",
    }.get(t, "Unknown")

    def mock_hist(ticker, period="1y"):
        n = 252
        if ticker in ("AAPL", "MSFT", "SPY"):
            return pd.Series([100.0 + i * 0.1 for i in range(n)])
        return pd.Series(dtype=float)

    provider.get_historical_prices.side_effect = mock_hist
    return provider


class TestAnalyzeCommand:
    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_csv(self, mock_provider_cls, runner, sample_csv, mock_market):
        mock_provider_cls.return_value = mock_market
        result = runner.invoke(cli, [
            "analyze", str(sample_csv), "--no-ai",
        ])
        assert result.exit_code == 0
        assert "AAPL" in result.output

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_with_benchmark(self, mock_provider_cls, runner, sample_csv, mock_market):
        mock_provider_cls.return_value = mock_market
        result = runner.invoke(cli, [
            "analyze", str(sample_csv), "--benchmark", "SPY", "--no-ai",
        ])
        assert result.exit_code == 0

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_nonexistent_file(self, mock_provider_cls, runner):
        result = runner.invoke(cli, ["analyze", "nonexistent.csv", "--no-ai"])
        assert result.exit_code != 0

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_with_export(self, mock_provider_cls, runner, sample_csv, mock_market, tmp_path):
        mock_provider_cls.return_value = mock_market
        output = tmp_path / "result.xlsx"
        result = runner.invoke(cli, [
            "analyze", str(sample_csv), "--no-ai", "--export", str(output),
        ])
        assert result.exit_code == 0
        assert output.exists()


class TestRebalanceCommand:
    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_rebalance_basic(self, mock_provider_cls, runner, sample_csv, mock_market, tmp_path):
        mock_provider_cls.return_value = mock_market
        target_csv = tmp_path / "target.csv"
        target_csv.write_text("ticker,weight\nAAPL,40.0\nMSFT,60.0\n")
        result = runner.invoke(cli, [
            "rebalance", str(sample_csv), "--target", str(target_csv), "--no-ai",
        ])
        assert result.exit_code == 0

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_rebalance_with_tolerance(self, mock_provider_cls, runner, sample_csv, mock_market, tmp_path):
        mock_provider_cls.return_value = mock_market
        target_csv = tmp_path / "target.csv"
        target_csv.write_text("ticker,weight\nAAPL,40.0\nMSFT,60.0\n")
        result = runner.invoke(cli, [
            "rebalance", str(sample_csv), "--target", str(target_csv),
            "--tolerance", "2.0", "--no-ai",
        ])
        assert result.exit_code == 0
