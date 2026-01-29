"""Terminal output formatters."""

from __future__ import annotations

from portfolio_ai.core.models import AnalysisResult, HoldingAnalysis

CURRENCY_SYMBOLS = {
    "USD": "$",
    "KRW": "KRW ",
}


def format_currency(value: float, currency: str) -> str:
    """Format a value as currency."""
    symbol = CURRENCY_SYMBOLS.get(currency, currency + " ")
    if currency == "KRW":
        if value < 0:
            return f"-{symbol}{abs(value):,.0f}"
        return f"{symbol}{value:,.0f}"
    if value < 0:
        return f"-{symbol}{abs(value):,.2f}"
    return f"{symbol}{value:,.2f}"


def format_percent(value: float) -> str:
    """Format a value as percentage with sign."""
    if value > 0:
        return f"+{value:.2f}%"
    elif value < 0:
        return f"{value:.2f}%"
    return "0.00%"


def format_holdings_table(
    holdings: tuple[HoldingAnalysis, ...],
    currency: str,
) -> str:
    """Format holdings as a text table."""
    header = f"{'Ticker':<10} {'Name':<20} {'Qty':>8} {'Avg Cost':>12} {'Price':>12} {'Value':>14} {'Weight':>8} {'Return':>10} {'Sector':<15}"
    separator = "-" * len(header)
    lines = [header, separator]

    for h in holdings:
        lines.append(
            f"{h.ticker:<10} {h.name:<20} {h.quantity:>8.0f} "
            f"{format_currency(h.avg_cost, currency):>12} "
            f"{format_currency(h.current_price, currency):>12} "
            f"{format_currency(h.market_value, currency):>14} "
            f"{h.weight_pct:>7.1f}% "
            f"{format_percent(h.return_pct):>10} "
            f"{h.sector:<15}"
        )

    return "\n".join(lines)


def format_summary(result: AnalysisResult) -> str:
    """Format analysis result as a summary string."""
    c = result.currency
    lines = [
        f"{'=' * 60}",
        f"  Portfolio: {result.portfolio_name}",
        f"  Benchmark: {result.benchmark_ticker}",
        f"{'=' * 60}",
        "",
        f"  Total Value:        {format_currency(result.total_value, c)}",
        f"  Total Cost:         {format_currency(result.total_cost, c)}",
        f"  Profit/Loss:        {format_currency(result.profit_loss, c)}",
        "",
        f"  Total Return:       {format_percent(result.total_return_pct)}",
        f"  Annualized Return:  {format_percent(result.annualized_return_pct)}",
        f"  Volatility:         {result.volatility_pct:.2f}%",
        f"  Sharpe Ratio:       {result.sharpe_ratio:.2f}",
        f"  Max Drawdown:       {result.max_drawdown_pct:.2f}%",
        f"  Beta:               {result.beta:.2f}",
        f"  Alpha:              {format_percent(result.alpha_pct)}",
        f"{'=' * 60}",
    ]
    return "\n".join(lines)
