"""CLI command implementations."""

from __future__ import annotations

import os
from pathlib import Path

import click
import pandas as pd
from dotenv import load_dotenv

from portfolio_ai.core.ai_insights import generate_insights
from portfolio_ai.core.analyzer import PortfolioAnalyzer
from portfolio_ai.core.rebalancer import rebalance
from portfolio_ai.data.exporter import export_to_excel
from portfolio_ai.data.loader import load_portfolio
from portfolio_ai.data.market_data import MarketDataProvider
from portfolio_ai.utils.formatters import (
    format_currency,
    format_holdings_table,
    format_percent,
    format_summary,
)

load_dotenv()


def run_analyze(
    file: str,
    *,
    name: str,
    currency: str,
    benchmark: str,
    no_ai: bool,
    export: str | None,
) -> None:
    """Run portfolio analysis."""
    path = Path(file)
    portfolio = load_portfolio(path, name=name, currency=currency)
    click.echo(f"Loaded {len(portfolio.holdings)} holdings from {path.name}")

    market = MarketDataProvider()
    analyzer = PortfolioAnalyzer(market_data=market)
    result = analyzer.analyze(portfolio, benchmark=benchmark)

    click.echo("")
    click.echo(format_summary(result))
    click.echo("")
    click.echo(format_holdings_table(result.holdings_analysis, currency))

    if not no_ai:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        click.echo("\nGenerating AI insights...")
        insights = generate_insights(result, api_key=api_key)
        click.echo(f"\n{insights}")

    if export:
        export_path = Path(export)
        export_to_excel(result, export_path)
        click.echo(f"\nExported to {export_path}")


def run_rebalance(
    file: str,
    *,
    target: str,
    name: str,
    currency: str,
    benchmark: str,
    tolerance: float,
    tax_rate: float,
    no_ai: bool,
    export: str | None,
) -> None:
    """Run portfolio rebalancing."""
    path = Path(file)
    portfolio = load_portfolio(path, name=name, currency=currency)
    click.echo(f"Loaded {len(portfolio.holdings)} holdings from {path.name}")

    market = MarketDataProvider()
    analyzer = PortfolioAnalyzer(market_data=market)
    result = analyzer.analyze(portfolio, benchmark=benchmark)

    target_df = pd.read_csv(target)
    target_weights = dict(zip(target_df["ticker"], target_df["weight"]))

    click.echo(f"\nTarget weights: {target_weights}")
    click.echo(f"Tolerance: {tolerance}%")

    rebalance_result = rebalance(
        holdings=result.holdings_analysis,
        target_weights=target_weights,
        total_value=result.total_value,
        tolerance=tolerance,
        tax_rate=tax_rate,
    )

    if not rebalance_result.orders:
        click.echo("\nPortfolio is within tolerance. No rebalancing needed.")
        return

    click.echo(f"\nRebalance Orders:")
    click.echo(f"{'Action':<6} {'Ticker':<10} {'Qty':>8} {'Price':>12} {'Cost':>14}")
    click.echo("-" * 52)

    for order in rebalance_result.orders:
        click.echo(
            f"{order.action:<6} {order.ticker:<10} {order.quantity:>8} "
            f"{format_currency(order.current_price, currency):>12} "
            f"{format_currency(order.estimated_cost, currency):>14}"
        )

    click.echo(f"\nTotal Buy:  {format_currency(rebalance_result.total_buy_cost, currency)}")
    click.echo(f"Total Sell: {format_currency(rebalance_result.total_sell_proceeds, currency)}")
    click.echo(f"Net Cost:   {format_currency(rebalance_result.net_cost, currency)}")

    if rebalance_result.estimated_tax > 0:
        click.echo(f"Est. Tax:   {format_currency(rebalance_result.estimated_tax, currency)}")

    if export:
        export_path = Path(export)
        export_to_excel(result, export_path)
        click.echo(f"\nExported to {export_path}")
