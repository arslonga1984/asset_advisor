"""Tests for portfolio rebalancer."""

import pytest

from portfolio_ai.core.models import Holding, HoldingAnalysis, Portfolio
from portfolio_ai.core.rebalancer import (
    RebalanceOrder,
    RebalanceResult,
    rebalance,
)


@pytest.fixture
def current_holdings():
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
            name="Microsoft Corp.",
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
def target_weights():
    return {"AAPL": 40.0, "MSFT": 60.0}


class TestRebalanceOrder:
    def test_create_buy_order(self):
        order = RebalanceOrder(
            ticker="AAPL",
            name="Apple Inc.",
            action="BUY",
            quantity=5,
            current_price=175.0,
            estimated_cost=875.0,
        )
        assert order.action == "BUY"
        assert order.estimated_cost == 875.0

    def test_create_sell_order(self):
        order = RebalanceOrder(
            ticker="AAPL",
            name="Apple Inc.",
            action="SELL",
            quantity=3,
            current_price=175.0,
            estimated_cost=-525.0,
        )
        assert order.action == "SELL"

    def test_order_is_frozen(self):
        order = RebalanceOrder(
            ticker="AAPL",
            name="Apple Inc.",
            action="BUY",
            quantity=5,
            current_price=175.0,
            estimated_cost=875.0,
        )
        with pytest.raises(AttributeError):
            order.quantity = 10


class TestRebalanceResult:
    def test_create_result(self):
        orders = (
            RebalanceOrder("AAPL", "Apple", "SELL", 2, 175.0, -350.0),
            RebalanceOrder("MSFT", "Microsoft", "BUY", 1, 350.0, 350.0),
        )
        result = RebalanceResult(
            orders=orders,
            total_buy_cost=350.0,
            total_sell_proceeds=350.0,
            net_cost=0.0,
            estimated_tax=0.0,
        )
        assert len(result.orders) == 2
        assert result.net_cost == 0.0

    def test_result_is_frozen(self):
        result = RebalanceResult(
            orders=(),
            total_buy_cost=0.0,
            total_sell_proceeds=0.0,
            net_cost=0.0,
            estimated_tax=0.0,
        )
        with pytest.raises(AttributeError):
            result.net_cost = 100.0


class TestRebalance:
    def test_rebalance_generates_orders(self, current_holdings, target_weights):
        result = rebalance(
            holdings=current_holdings,
            target_weights=target_weights,
            total_value=3500.0,
        )
        assert isinstance(result, RebalanceResult)
        assert len(result.orders) > 0

    def test_rebalance_sell_overweight(self, current_holdings, target_weights):
        result = rebalance(
            holdings=current_holdings,
            target_weights=target_weights,
            total_value=3500.0,
        )
        aapl_order = next(o for o in result.orders if o.ticker == "AAPL")
        assert aapl_order.action == "SELL"

    def test_rebalance_buy_underweight(self, current_holdings, target_weights):
        result = rebalance(
            holdings=current_holdings,
            target_weights=target_weights,
            total_value=3500.0,
        )
        msft_order = next(o for o in result.orders if o.ticker == "MSFT")
        assert msft_order.action == "BUY"

    def test_rebalance_within_tolerance_no_orders(self, current_holdings):
        target = {"AAPL": 50.0, "MSFT": 50.0}
        result = rebalance(
            holdings=current_holdings,
            target_weights=target,
            total_value=3500.0,
            tolerance=5.0,
        )
        assert len(result.orders) == 0

    def test_rebalance_total_costs(self, current_holdings, target_weights):
        result = rebalance(
            holdings=current_holdings,
            target_weights=target_weights,
            total_value=3500.0,
        )
        assert result.total_buy_cost >= 0
        assert result.total_sell_proceeds >= 0

    def test_rebalance_with_tax_estimation(self, current_holdings, target_weights):
        result = rebalance(
            holdings=current_holdings,
            target_weights=target_weights,
            total_value=3500.0,
            tax_rate=0.22,
        )
        assert result.estimated_tax >= 0
