"""Tests for portfolio analyzer."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from portfolio_ai.core.analyzer import PortfolioAnalyzer
from portfolio_ai.core.models import AnalysisResult, Holding, Portfolio


@pytest.fixture
def sample_portfolio():
    holdings = (
        Holding("AAPL", "Apple Inc.", 10, 150.0, "USD"),
        Holding("MSFT", "Microsoft Corp.", 5, 300.0, "USD"),
    )
    return Portfolio(name="Test Portfolio", holdings=holdings, currency="USD")


@pytest.fixture
def mock_market_data():
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

    np.random.seed(42)

    def mock_historical(ticker, period="1y"):
        n = 252
        idx = pd.RangeIndex(n)
        if ticker == "AAPL":
            return pd.Series([150.0 + i * 0.1 for i in range(n)], index=idx)
        elif ticker == "MSFT":
            return pd.Series([300.0 + i * 0.2 for i in range(n)], index=idx)
        elif ticker == "SPY":
            return pd.Series([400.0 + i * 0.15 for i in range(n)], index=idx)
        return pd.Series(dtype=float)

    provider.get_historical_prices.side_effect = mock_historical
    return provider


class TestPortfolioAnalyzer:
    def test_analyze_returns_result(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        assert isinstance(result, AnalysisResult)

    def test_analyze_portfolio_name(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        assert result.portfolio_name == "Test Portfolio"

    def test_analyze_total_value(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        expected = (10 * 175.0) + (5 * 350.0)
        assert result.total_value == pytest.approx(expected)

    def test_analyze_total_cost(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        expected = (10 * 150.0) + (5 * 300.0)
        assert result.total_cost == pytest.approx(expected)

    def test_analyze_holdings_analysis(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        assert len(result.holdings_analysis) == 2
        aapl = result.holdings_analysis[0]
        assert aapl.ticker == "AAPL"
        assert aapl.current_price == 175.0
        assert aapl.sector == "Technology"

    def test_analyze_weights(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        total_weight = sum(h.weight_pct for h in result.holdings_analysis)
        assert total_weight == pytest.approx(100.0, abs=0.1)

    def test_analyze_benchmark(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        assert result.benchmark_ticker == "SPY"

    def test_analyze_no_ai_insights(self, sample_portfolio, mock_market_data):
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(sample_portfolio, benchmark="SPY")
        assert result.ai_insights is None

    def test_analyze_missing_price_skips_holding(self, mock_market_data):
        mock_market_data.get_current_price.side_effect = lambda t: {
            "AAPL": 175.0,
        }.get(t)
        holdings = (
            Holding("AAPL", "Apple Inc.", 10, 150.0, "USD"),
            Holding("FAKE", "Fake Corp.", 5, 100.0, "USD"),
        )
        portfolio = Portfolio(name="Test", holdings=holdings, currency="USD")
        analyzer = PortfolioAnalyzer(market_data=mock_market_data)
        result = analyzer.analyze(portfolio, benchmark="SPY")
        assert len(result.holdings_analysis) == 1
