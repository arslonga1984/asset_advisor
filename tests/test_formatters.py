"""Tests for output formatters."""

import pytest

from portfolio_ai.utils.formatters import (
    format_currency,
    format_percent,
    format_holdings_table,
    format_summary,
)
from portfolio_ai.core.models import AnalysisResult, HoldingAnalysis


@pytest.fixture
def sample_holdings():
    return (
        HoldingAnalysis(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_cost=150.0,
            current_price=175.0,
            market_value=1750.0,
            weight_pct=50.0,
            return_pct=16.67,
            sector="Technology",
        ),
        HoldingAnalysis(
            ticker="MSFT",
            name="Microsoft",
            quantity=5,
            avg_cost=300.0,
            current_price=350.0,
            market_value=1750.0,
            weight_pct=50.0,
            return_pct=16.67,
            sector="Technology",
        ),
    )


@pytest.fixture
def sample_result(sample_holdings):
    return AnalysisResult(
        portfolio_name="Test Portfolio",
        total_value=3500.0,
        total_cost=3000.0,
        total_return_pct=16.67,
        annualized_return_pct=16.67,
        volatility_pct=20.0,
        sharpe_ratio=0.73,
        max_drawdown_pct=-8.0,
        beta=1.1,
        alpha_pct=2.0,
        currency="USD",
        holdings_analysis=sample_holdings,
        benchmark_ticker="SPY",
    )


class TestFormatCurrency:
    def test_usd(self):
        assert format_currency(1234.56, "USD") == "$1,234.56"

    def test_krw(self):
        assert format_currency(1234567, "KRW") == "KRW 1,234,567"

    def test_large_usd(self):
        assert format_currency(1000000.0, "USD") == "$1,000,000.00"

    def test_negative(self):
        assert format_currency(-500.0, "USD") == "-$500.00"


class TestFormatPercent:
    def test_positive(self):
        assert format_percent(16.67) == "+16.67%"

    def test_negative(self):
        assert format_percent(-8.0) == "-8.00%"

    def test_zero(self):
        assert format_percent(0.0) == "0.00%"


class TestFormatHoldingsTable:
    def test_returns_string(self, sample_holdings):
        result = format_holdings_table(sample_holdings, "USD")
        assert isinstance(result, str)
        assert "AAPL" in result
        assert "MSFT" in result

    def test_contains_headers(self, sample_holdings):
        result = format_holdings_table(sample_holdings, "USD")
        assert "Ticker" in result or "ticker" in result.lower()


class TestFormatSummary:
    def test_returns_string(self, sample_result):
        result = format_summary(sample_result)
        assert isinstance(result, str)

    def test_contains_portfolio_name(self, sample_result):
        result = format_summary(sample_result)
        assert "Test Portfolio" in result

    def test_contains_metrics(self, sample_result):
        result = format_summary(sample_result)
        assert "16.67" in result  # return
        assert "0.73" in result   # sharpe
