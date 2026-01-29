"""Portfolio analysis engine."""

from __future__ import annotations

import numpy as np
import pandas as pd

from portfolio_ai.core.models import (
    AnalysisResult,
    HoldingAnalysis,
    Portfolio,
)
from portfolio_ai.data.market_data import MarketDataProvider
from portfolio_ai.utils.metrics import (
    alpha,
    annualized_return,
    beta,
    max_drawdown,
    sharpe_ratio,
    total_return,
    volatility,
)


class PortfolioAnalyzer:
    """Analyzes a portfolio and produces an AnalysisResult."""

    def __init__(self, market_data: MarketDataProvider | None = None) -> None:
        self._market = market_data or MarketDataProvider()

    def analyze(
        self,
        portfolio: Portfolio,
        *,
        benchmark: str = "SPY",
    ) -> AnalysisResult:
        """Analyze a portfolio and return results."""
        holdings_data = self._gather_holdings_data(portfolio)
        if not holdings_data:
            return self._empty_result(portfolio, benchmark)

        total_value = sum(h.market_value for h in holdings_data)
        total_cost = sum(h.avg_cost * h.quantity for h in holdings_data)

        holdings_analysis = tuple(
            HoldingAnalysis(
                ticker=h.ticker,
                name=h.name,
                quantity=h.quantity,
                avg_cost=h.avg_cost,
                current_price=h.current_price,
                market_value=h.market_value,
                weight_pct=(h.market_value / total_value) * 100 if total_value > 0 else 0,
                return_pct=((h.current_price - h.avg_cost) / h.avg_cost) * 100,
                sector=h.sector,
            )
            for h in holdings_data
        )

        portfolio_returns = self._compute_portfolio_returns(holdings_analysis, portfolio)
        benchmark_returns = self._get_benchmark_returns(benchmark)

        total_ret = total_return(initial=total_cost, final=total_value)
        ann_ret = annualized_return(total_return_pct=total_ret, years=1.0)
        vol = volatility(portfolio_returns)
        sr = sharpe_ratio(portfolio_returns)
        mdd = self._compute_max_drawdown(holdings_analysis, portfolio)
        b = beta(portfolio_returns, benchmark_returns)

        benchmark_total_ret = self._compute_benchmark_total_return(benchmark)
        a = alpha(
            portfolio_return=ann_ret,
            benchmark_return=benchmark_total_ret,
            beta_value=b,
        )

        return AnalysisResult(
            portfolio_name=portfolio.name,
            total_value=total_value,
            total_cost=total_cost,
            total_return_pct=total_ret,
            annualized_return_pct=ann_ret,
            volatility_pct=vol * 100,
            sharpe_ratio=sr,
            max_drawdown_pct=mdd,
            beta=b,
            alpha_pct=a,
            currency=portfolio.currency,
            holdings_analysis=holdings_analysis,
            benchmark_ticker=benchmark,
        )

    def _gather_holdings_data(self, portfolio: Portfolio) -> list[_HoldingData]:
        results = []
        for holding in portfolio.holdings:
            price = self._market.get_current_price(holding.ticker)
            if price is None:
                continue
            sector = self._market.get_sector(holding.ticker)
            results.append(
                _HoldingData(
                    ticker=holding.ticker,
                    name=holding.name,
                    quantity=holding.quantity,
                    avg_cost=holding.avg_cost,
                    current_price=price,
                    market_value=holding.quantity * price,
                    sector=sector,
                )
            )
        return results

    def _compute_portfolio_returns(
        self,
        holdings_analysis: tuple[HoldingAnalysis, ...],
        portfolio: Portfolio,
    ) -> pd.Series:
        all_prices = {}
        for h in holdings_analysis:
            prices = self._market.get_historical_prices(h.ticker)
            if not prices.empty:
                all_prices[h.ticker] = prices

        if not all_prices:
            return pd.Series(dtype=float)

        price_df = pd.DataFrame(all_prices).dropna()
        if price_df.empty:
            return pd.Series(dtype=float)

        weights = np.array([h.weight_pct / 100 for h in holdings_analysis if h.ticker in all_prices])
        returns_df = price_df.pct_change().dropna()

        if returns_df.empty:
            return pd.Series(dtype=float)

        portfolio_returns = returns_df.dot(weights)
        return portfolio_returns

    def _get_benchmark_returns(self, benchmark: str) -> pd.Series:
        prices = self._market.get_historical_prices(benchmark)
        if prices.empty:
            return pd.Series(dtype=float)
        return prices.pct_change().dropna()

    def _compute_max_drawdown(
        self,
        holdings_analysis: tuple[HoldingAnalysis, ...],
        portfolio: Portfolio,
    ) -> float:
        all_prices = {}
        for h in holdings_analysis:
            prices = self._market.get_historical_prices(h.ticker)
            if not prices.empty:
                all_prices[h.ticker] = prices

        if not all_prices:
            return 0.0

        price_df = pd.DataFrame(all_prices).dropna()
        if price_df.empty:
            return 0.0

        weights = np.array([h.weight_pct / 100 for h in holdings_analysis if h.ticker in all_prices])
        portfolio_value = price_df.dot(weights)
        return max_drawdown(portfolio_value)

    def _compute_benchmark_total_return(self, benchmark: str) -> float:
        prices = self._market.get_historical_prices(benchmark)
        if prices.empty or len(prices) < 2:
            return 0.0
        return total_return(initial=float(prices.iloc[0]), final=float(prices.iloc[-1]))

    def _empty_result(self, portfolio: Portfolio, benchmark: str) -> AnalysisResult:
        return AnalysisResult(
            portfolio_name=portfolio.name,
            total_value=0.0,
            total_cost=portfolio.total_cost,
            total_return_pct=0.0,
            annualized_return_pct=0.0,
            volatility_pct=0.0,
            sharpe_ratio=0.0,
            max_drawdown_pct=0.0,
            beta=0.0,
            alpha_pct=0.0,
            currency=portfolio.currency,
            holdings_analysis=(),
            benchmark_ticker=benchmark,
        )


class _HoldingData:
    """Temporary internal data holder for gathering market data."""

    __slots__ = ("ticker", "name", "quantity", "avg_cost", "current_price", "market_value", "sector")

    def __init__(
        self,
        ticker: str,
        name: str,
        quantity: float,
        avg_cost: float,
        current_price: float,
        market_value: float,
        sector: str,
    ) -> None:
        self.ticker = ticker
        self.name = name
        self.quantity = quantity
        self.avg_cost = avg_cost
        self.current_price = current_price
        self.market_value = market_value
        self.sector = sector
