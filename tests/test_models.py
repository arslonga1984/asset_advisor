"""Tests for data models."""

from datetime import date

import pytest

from portfolio_ai.core.models import (
    AnalysisResult,
    Holding,
    Portfolio,
)


class TestHolding:
    def test_create_us_holding(self):
        holding = Holding(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_cost=150.0,
            currency="USD",
        )
        assert holding.ticker == "AAPL"
        assert holding.name == "Apple Inc."
        assert holding.quantity == 10
        assert holding.avg_cost == 150.0
        assert holding.currency == "USD"

    def test_create_kr_holding(self):
        holding = Holding(
            ticker="005930.KS",
            name="삼성전자",
            quantity=100,
            avg_cost=70000.0,
            currency="KRW",
        )
        assert holding.ticker == "005930.KS"
        assert holding.currency == "KRW"

    def test_holding_is_frozen(self):
        holding = Holding(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_cost=150.0,
            currency="USD",
        )
        with pytest.raises(AttributeError):
            holding.quantity = 20

    def test_holding_total_cost(self):
        holding = Holding(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_cost=150.0,
            currency="USD",
        )
        assert holding.total_cost == 1500.0

    def test_holding_default_currency(self):
        holding = Holding(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_cost=150.0,
        )
        assert holding.currency == "USD"


class TestPortfolio:
    def test_create_portfolio(self):
        holdings = (
            Holding("AAPL", "Apple", 10, 150.0, "USD"),
            Holding("GOOGL", "Google", 5, 2800.0, "USD"),
        )
        portfolio = Portfolio(
            name="My Portfolio",
            holdings=holdings,
            currency="USD",
        )
        assert portfolio.name == "My Portfolio"
        assert len(portfolio.holdings) == 2
        assert portfolio.currency == "USD"

    def test_portfolio_is_frozen(self):
        portfolio = Portfolio(
            name="Test",
            holdings=(),
            currency="USD",
        )
        with pytest.raises(AttributeError):
            portfolio.name = "Changed"

    def test_portfolio_holdings_is_tuple(self):
        holdings = (
            Holding("AAPL", "Apple", 10, 150.0, "USD"),
        )
        portfolio = Portfolio(
            name="Test",
            holdings=holdings,
            currency="USD",
        )
        assert isinstance(portfolio.holdings, tuple)

    def test_portfolio_total_cost(self):
        holdings = (
            Holding("AAPL", "Apple", 10, 150.0, "USD"),
            Holding("GOOGL", "Google", 5, 100.0, "USD"),
        )
        portfolio = Portfolio(
            name="Test",
            holdings=holdings,
            currency="USD",
        )
        assert portfolio.total_cost == 2000.0

    def test_portfolio_default_date(self):
        portfolio = Portfolio(
            name="Test",
            holdings=(),
            currency="USD",
        )
        assert portfolio.as_of_date == date.today()

    def test_portfolio_custom_date(self):
        d = date(2024, 1, 15)
        portfolio = Portfolio(
            name="Test",
            holdings=(),
            currency="USD",
            as_of_date=d,
        )
        assert portfolio.as_of_date == d


class TestAnalysisResult:
    def test_create_analysis_result(self):
        result = AnalysisResult(
            portfolio_name="Test Portfolio",
            total_value=100000.0,
            total_cost=80000.0,
            total_return_pct=25.0,
            annualized_return_pct=12.5,
            volatility_pct=15.0,
            sharpe_ratio=0.83,
            max_drawdown_pct=-10.0,
            beta=1.1,
            alpha_pct=2.0,
            currency="USD",
            holdings_analysis=(),
            benchmark_ticker="SPY",
        )
        assert result.portfolio_name == "Test Portfolio"
        assert result.total_value == 100000.0
        assert result.total_return_pct == 25.0
        assert result.sharpe_ratio == 0.83

    def test_analysis_result_is_frozen(self):
        result = AnalysisResult(
            portfolio_name="Test",
            total_value=100000.0,
            total_cost=80000.0,
            total_return_pct=25.0,
            annualized_return_pct=12.5,
            volatility_pct=15.0,
            sharpe_ratio=0.83,
            max_drawdown_pct=-10.0,
            beta=1.1,
            alpha_pct=2.0,
            currency="USD",
            holdings_analysis=(),
            benchmark_ticker="SPY",
        )
        with pytest.raises(AttributeError):
            result.total_value = 200000.0

    def test_analysis_result_profit_loss(self):
        result = AnalysisResult(
            portfolio_name="Test",
            total_value=100000.0,
            total_cost=80000.0,
            total_return_pct=25.0,
            annualized_return_pct=12.5,
            volatility_pct=15.0,
            sharpe_ratio=0.83,
            max_drawdown_pct=-10.0,
            beta=1.1,
            alpha_pct=2.0,
            currency="USD",
            holdings_analysis=(),
            benchmark_ticker="SPY",
        )
        assert result.profit_loss == 20000.0

    def test_analysis_result_optional_ai_insights(self):
        result = AnalysisResult(
            portfolio_name="Test",
            total_value=100000.0,
            total_cost=80000.0,
            total_return_pct=25.0,
            annualized_return_pct=12.5,
            volatility_pct=15.0,
            sharpe_ratio=0.83,
            max_drawdown_pct=-10.0,
            beta=1.1,
            alpha_pct=2.0,
            currency="USD",
            holdings_analysis=(),
            benchmark_ticker="SPY",
        )
        assert result.ai_insights is None

    def test_analysis_result_with_ai_insights(self):
        result = AnalysisResult(
            portfolio_name="Test",
            total_value=100000.0,
            total_cost=80000.0,
            total_return_pct=25.0,
            annualized_return_pct=12.5,
            volatility_pct=15.0,
            sharpe_ratio=0.83,
            max_drawdown_pct=-10.0,
            beta=1.1,
            alpha_pct=2.0,
            currency="USD",
            holdings_analysis=(),
            benchmark_ticker="SPY",
            ai_insights="Portfolio is well-diversified.",
        )
        assert result.ai_insights == "Portfolio is well-diversified."
