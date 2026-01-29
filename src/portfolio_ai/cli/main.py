"""CLI entry point for portfolio-ai."""

from __future__ import annotations

import click

from portfolio_ai.cli.commands import run_analyze, run_rebalance


@click.group()
@click.version_option(package_name="portfolio-ai")
def cli() -> None:
    """AI-powered investment portfolio analysis tool."""


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--name", default="My Portfolio", help="Portfolio name")
@click.option("--currency", default="USD", help="Portfolio currency (USD/KRW)")
@click.option("--benchmark", default="SPY", help="Benchmark ticker")
@click.option("--no-ai", is_flag=True, help="Disable AI insights")
@click.option("--export", default=None, help="Export to Excel file path")
def analyze(
    file: str,
    name: str,
    currency: str,
    benchmark: str,
    no_ai: bool,
    export: str | None,
) -> None:
    """Analyze a portfolio from CSV/Excel file."""
    run_analyze(
        file,
        name=name,
        currency=currency,
        benchmark=benchmark,
        no_ai=no_ai,
        export=export,
    )


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--target", required=True, help="Target weights CSV file")
@click.option("--name", default="My Portfolio", help="Portfolio name")
@click.option("--currency", default="USD", help="Portfolio currency")
@click.option("--benchmark", default="SPY", help="Benchmark ticker")
@click.option("--tolerance", default=1.0, help="Rebalance tolerance (%)")
@click.option("--tax-rate", default=0.0, help="Estimated tax rate for gains")
@click.option("--no-ai", is_flag=True, help="Disable AI insights")
@click.option("--export", default=None, help="Export to Excel file path")
def rebalance(
    file: str,
    target: str,
    name: str,
    currency: str,
    benchmark: str,
    tolerance: float,
    tax_rate: float,
    no_ai: bool,
    export: str | None,
) -> None:
    """Rebalance a portfolio to target weights."""
    run_rebalance(
        file,
        target=target,
        name=name,
        currency=currency,
        benchmark=benchmark,
        tolerance=tolerance,
        tax_rate=tax_rate,
        no_ai=no_ai,
        export=export,
    )
