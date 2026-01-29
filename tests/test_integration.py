"""Integration tests: full pipeline from file to analysis output."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from click.testing import CliRunner

from portfolio_ai.cli.main import cli
from portfolio_ai.core.analyzer import PortfolioAnalyzer
from portfolio_ai.core.models import AnalysisResult
from portfolio_ai.data.exporter import export_to_excel
from portfolio_ai.data.loader import load_portfolio


def _mock_market_provider():
    """Create a mocked MarketDataProvider for integration tests."""
    provider = MagicMock()

    prices = {
        "AAPL": 190.0,
        "MSFT": 420.0,
        "GOOGL": 175.0,
        "NVDA": 880.0,
        "META": 500.0,
        "005930.KS": 75000.0,
        "000660.KS": 160000.0,
        "035420.KS": 200000.0,
        "005380.KS": 240000.0,
        "051910.KS": 450000.0,
        "SPY": 520.0,
        "^KS11": 2650.0,
    }
    sectors = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Communication Services",
        "NVDA": "Technology",
        "META": "Communication Services",
        "005930.KS": "Technology",
        "000660.KS": "Technology",
        "035420.KS": "Communication Services",
        "005380.KS": "Consumer Cyclical",
        "051910.KS": "Basic Materials",
    }

    provider.get_current_price.side_effect = lambda t: prices.get(t)
    provider.get_sector.side_effect = lambda t: sectors.get(t, "Unknown")

    def mock_hist(ticker, period="1y"):
        base = prices.get(ticker)
        if base is None:
            return pd.Series(dtype=float)
        n = 252
        return pd.Series([base * (0.9 + 0.2 * i / n) for i in range(n)])

    provider.get_historical_prices.side_effect = mock_hist
    return provider


class TestUSPortfolioIntegration:
    """Full pipeline test with US tech portfolio."""

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_us_portfolio_cli(self, mock_cls):
        mock_cls.return_value = _mock_market_provider()
        runner = CliRunner()
        result = runner.invoke(cli, [
            "analyze",
            "data/samples/us_tech_portfolio.csv",
            "--benchmark", "SPY",
            "--no-ai",
        ])
        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "NVDA" in result.output

    def test_load_and_analyze_us_portfolio(self):
        path = Path("data/samples/us_tech_portfolio.csv")
        portfolio = load_portfolio(path, name="US Tech", currency="USD")

        assert len(portfolio.holdings) == 5
        assert portfolio.currency == "USD"

        market = _mock_market_provider()
        analyzer = PortfolioAnalyzer(market_data=market)
        result = analyzer.analyze(portfolio, benchmark="SPY")

        assert isinstance(result, AnalysisResult)
        assert result.total_value > 0
        assert len(result.holdings_analysis) == 5

    def test_analyze_and_export_us_portfolio(self, tmp_path: Path):
        path = Path("data/samples/us_tech_portfolio.csv")
        portfolio = load_portfolio(path, name="US Tech", currency="USD")

        market = _mock_market_provider()
        analyzer = PortfolioAnalyzer(market_data=market)
        result = analyzer.analyze(portfolio, benchmark="SPY")

        output = tmp_path / "us_tech_output.xlsx"
        export_to_excel(result, output)
        assert output.exists()


class TestKRPortfolioIntegration:
    """Full pipeline test with Korean blue chip portfolio."""

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_kr_portfolio_cli(self, mock_cls):
        mock_cls.return_value = _mock_market_provider()
        runner = CliRunner()
        result = runner.invoke(cli, [
            "analyze",
            "data/samples/kr_blue_chip.csv",
            "--currency", "KRW",
            "--benchmark", "^KS11",
            "--no-ai",
        ])
        assert result.exit_code == 0
        assert "005930.KS" in result.output

    def test_load_and_analyze_kr_portfolio(self):
        path = Path("data/samples/kr_blue_chip.csv")
        portfolio = load_portfolio(path, name="KR Blue Chip", currency="KRW")

        assert len(portfolio.holdings) == 5
        assert portfolio.currency == "KRW"

        market = _mock_market_provider()
        analyzer = PortfolioAnalyzer(market_data=market)
        result = analyzer.analyze(portfolio, benchmark="^KS11")

        assert isinstance(result, AnalysisResult)
        assert result.total_value > 0


class TestMixedPortfolioIntegration:
    """Full pipeline test with mixed global portfolio."""

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_analyze_mixed_portfolio_cli(self, mock_cls):
        mock_cls.return_value = _mock_market_provider()
        runner = CliRunner()
        result = runner.invoke(cli, [
            "analyze",
            "data/samples/mixed_global.csv",
            "--no-ai",
        ])
        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "005930.KS" in result.output

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_rebalance_mixed_portfolio_cli(self, mock_cls, tmp_path: Path):
        mock_cls.return_value = _mock_market_provider()
        target_csv = tmp_path / "target.csv"
        target_csv.write_text(
            "ticker,weight\nAAPL,25.0\nMSFT,25.0\n005930.KS,20.0\n000660.KS,15.0\nGOOGL,15.0\n"
        )
        runner = CliRunner()
        result = runner.invoke(cli, [
            "rebalance",
            "data/samples/mixed_global.csv",
            "--target", str(target_csv),
            "--no-ai",
        ])
        assert result.exit_code == 0


class TestEndToEndExport:
    """Test full file -> analyze -> export pipeline."""

    @patch("portfolio_ai.cli.commands.MarketDataProvider")
    def test_full_pipeline_with_export(self, mock_cls, tmp_path: Path):
        mock_cls.return_value = _mock_market_provider()
        output = tmp_path / "full_output.xlsx"
        runner = CliRunner()
        result = runner.invoke(cli, [
            "analyze",
            "data/samples/us_tech_portfolio.csv",
            "--no-ai",
            "--export", str(output),
        ])
        assert result.exit_code == 0
        assert output.exists()
        assert "Exported to" in result.output
