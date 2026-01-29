"""Portfolio rebalancing logic."""

from __future__ import annotations

import math
from dataclasses import dataclass

from portfolio_ai.core.models import HoldingAnalysis


@dataclass(frozen=True)
class RebalanceOrder:
    """A single rebalance order (BUY or SELL)."""

    ticker: str
    name: str
    action: str  # "BUY" or "SELL"
    quantity: int
    current_price: float
    estimated_cost: float  # positive for BUY, negative for SELL


@dataclass(frozen=True)
class RebalanceResult:
    """Complete rebalance calculation result."""

    orders: tuple[RebalanceOrder, ...]
    total_buy_cost: float
    total_sell_proceeds: float
    net_cost: float
    estimated_tax: float


def rebalance(
    *,
    holdings: tuple[HoldingAnalysis, ...],
    target_weights: dict[str, float],
    total_value: float,
    tolerance: float = 1.0,
    tax_rate: float = 0.0,
) -> RebalanceResult:
    """Calculate rebalance orders to reach target weights."""
    orders: list[RebalanceOrder] = []
    total_buy = 0.0
    total_sell = 0.0
    estimated_tax = 0.0

    for holding in holdings:
        target_pct = target_weights.get(holding.ticker, 0.0)
        diff_pct = target_pct - holding.weight_pct

        if abs(diff_pct) <= tolerance:
            continue

        target_value = total_value * (target_pct / 100)
        diff_value = target_value - holding.market_value

        quantity = int(math.floor(abs(diff_value) / holding.current_price))
        if quantity == 0:
            continue

        if diff_value > 0:
            cost = quantity * holding.current_price
            orders.append(
                RebalanceOrder(
                    ticker=holding.ticker,
                    name=holding.name,
                    action="BUY",
                    quantity=quantity,
                    current_price=holding.current_price,
                    estimated_cost=cost,
                )
            )
            total_buy += cost
        else:
            proceeds = quantity * holding.current_price
            gain_per_share = holding.current_price - holding.avg_cost
            if gain_per_share > 0 and tax_rate > 0:
                estimated_tax += quantity * gain_per_share * tax_rate

            orders.append(
                RebalanceOrder(
                    ticker=holding.ticker,
                    name=holding.name,
                    action="SELL",
                    quantity=quantity,
                    current_price=holding.current_price,
                    estimated_cost=-proceeds,
                )
            )
            total_sell += proceeds

    return RebalanceResult(
        orders=tuple(orders),
        total_buy_cost=total_buy,
        total_sell_proceeds=total_sell,
        net_cost=total_buy - total_sell,
        estimated_tax=estimated_tax,
    )
