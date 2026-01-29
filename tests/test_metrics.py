"""Tests for financial metrics."""

import numpy as np
import pandas as pd
import pytest

from portfolio_ai.utils.metrics import (
    alpha,
    annualized_return,
    beta,
    max_drawdown,
    sharpe_ratio,
    total_return,
    volatility,
)


@pytest.fixture
def daily_returns():
    """Simulated daily returns for 252 trading days."""
    np.random.seed(42)
    return pd.Series(np.random.normal(0.0005, 0.02, 252))


@pytest.fixture
def benchmark_returns():
    """Simulated benchmark daily returns."""
    np.random.seed(123)
    return pd.Series(np.random.normal(0.0004, 0.015, 252))


class TestTotalReturn:
    def test_positive_return(self):
        result = total_return(initial=100.0, final=120.0)
        assert result == pytest.approx(20.0)

    def test_negative_return(self):
        result = total_return(initial=100.0, final=80.0)
        assert result == pytest.approx(-20.0)

    def test_zero_return(self):
        result = total_return(initial=100.0, final=100.0)
        assert result == pytest.approx(0.0)

    def test_zero_initial_raises(self):
        with pytest.raises(ValueError, match="Initial value must be positive"):
            total_return(initial=0.0, final=100.0)


class TestAnnualizedReturn:
    def test_one_year(self):
        result = annualized_return(total_return_pct=10.0, years=1.0)
        assert result == pytest.approx(10.0)

    def test_two_years(self):
        result = annualized_return(total_return_pct=21.0, years=2.0)
        expected = ((1.21) ** (1 / 2) - 1) * 100
        assert result == pytest.approx(expected, rel=1e-4)

    def test_zero_years_raises(self):
        with pytest.raises(ValueError, match="Years must be positive"):
            annualized_return(total_return_pct=10.0, years=0.0)


class TestVolatility:
    def test_returns_positive_value(self, daily_returns):
        vol = volatility(daily_returns)
        assert vol > 0

    def test_annualized(self, daily_returns):
        vol = volatility(daily_returns, annualize=True)
        daily_vol = volatility(daily_returns, annualize=False)
        assert vol == pytest.approx(daily_vol * np.sqrt(252), rel=1e-4)

    def test_empty_returns(self):
        vol = volatility(pd.Series(dtype=float))
        assert vol == 0.0


class TestSharpeRatio:
    def test_positive_sharpe(self, daily_returns):
        sr = sharpe_ratio(daily_returns, risk_free_rate=0.02)
        assert isinstance(sr, float)

    def test_zero_volatility(self):
        constant_returns = pd.Series([0.001] * 100)
        sr = sharpe_ratio(constant_returns, risk_free_rate=0.0)
        assert sr == 0.0

    def test_empty_returns(self):
        sr = sharpe_ratio(pd.Series(dtype=float))
        assert sr == 0.0


class TestMaxDrawdown:
    def test_basic_drawdown(self):
        prices = pd.Series([100, 110, 90, 95, 80, 100])
        dd = max_drawdown(prices)
        expected = ((80 - 110) / 110) * 100
        assert dd == pytest.approx(expected, rel=1e-4)

    def test_no_drawdown(self):
        prices = pd.Series([100, 110, 120, 130])
        dd = max_drawdown(prices)
        assert dd == pytest.approx(0.0)

    def test_empty_prices(self):
        dd = max_drawdown(pd.Series(dtype=float))
        assert dd == 0.0


class TestBeta:
    def test_beta_calculation(self, daily_returns, benchmark_returns):
        b = beta(daily_returns, benchmark_returns)
        assert isinstance(b, float)

    def test_identical_returns(self):
        returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
        b = beta(returns, returns)
        assert b == pytest.approx(1.0, rel=1e-4)

    def test_empty_returns(self):
        b = beta(pd.Series(dtype=float), pd.Series(dtype=float))
        assert b == 0.0


class TestAlpha:
    def test_alpha_calculation(self):
        a = alpha(
            portfolio_return=15.0,
            benchmark_return=10.0,
            beta_value=1.2,
            risk_free_rate=2.0,
        )
        expected = 15.0 - (2.0 + 1.2 * (10.0 - 2.0))
        assert a == pytest.approx(expected, rel=1e-4)

    def test_zero_alpha(self):
        a = alpha(
            portfolio_return=10.0,
            benchmark_return=10.0,
            beta_value=1.0,
            risk_free_rate=0.0,
        )
        assert a == pytest.approx(0.0)
