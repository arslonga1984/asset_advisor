"""Core data models for portfolio analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Holding:
    """A single holding in a portfolio."""

    ticker: str
    name: str
    quantity: float
    avg_cost: float
    currency: str = "USD"

    @property
    def total_cost(self) -> float:
        return self.quantity * self.avg_cost


@dataclass(frozen=True)
class HoldingAnalysis:
    """Analysis result for a single holding."""

    ticker: str
    name: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    weight_pct: float
    return_pct: float
    sector: str = "Unknown"


@dataclass(frozen=True)
class Portfolio:
    """An investment portfolio containing holdings."""

    name: str
    holdings: tuple[Holding, ...]
    currency: str
    as_of_date: date = field(default_factory=date.today)

    @property
    def total_cost(self) -> float:
        return sum(h.total_cost for h in self.holdings)


@dataclass(frozen=True)
class AnalysisResult:
    """Complete portfolio analysis result."""

    portfolio_name: str
    total_value: float
    total_cost: float
    total_return_pct: float
    annualized_return_pct: float
    volatility_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    beta: float
    alpha_pct: float
    currency: str
    holdings_analysis: tuple[HoldingAnalysis, ...]
    benchmark_ticker: str
    ai_insights: str | None = None

    @property
    def profit_loss(self) -> float:
        return self.total_value - self.total_cost
