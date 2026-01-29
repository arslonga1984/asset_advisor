"""Financial metrics calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def total_return(*, initial: float, final: float) -> float:
    """Calculate total return percentage."""
    if initial <= 0:
        raise ValueError("Initial value must be positive")
    return ((final - initial) / initial) * 100


def annualized_return(*, total_return_pct: float, years: float) -> float:
    """Calculate annualized return from total return percentage."""
    if years <= 0:
        raise ValueError("Years must be positive")
    return ((1 + total_return_pct / 100) ** (1 / years) - 1) * 100


def volatility(
    returns: pd.Series,
    *,
    annualize: bool = True,
) -> float:
    """Calculate volatility (standard deviation) of returns."""
    if returns.empty:
        return 0.0
    std = returns.std()
    if annualize:
        return float(std * np.sqrt(252))
    return float(std)


def sharpe_ratio(
    returns: pd.Series,
    *,
    risk_free_rate: float = 0.02,
) -> float:
    """Calculate annualized Sharpe ratio."""
    if returns.empty:
        return 0.0
    vol = volatility(returns, annualize=True)
    if vol < 1e-10:
        return 0.0
    mean_return = float(returns.mean()) * 252
    return (mean_return - risk_free_rate) / vol


def max_drawdown(prices: pd.Series) -> float:
    """Calculate maximum drawdown percentage from a price series."""
    if prices.empty:
        return 0.0
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    return float(drawdown.min()) * 100


def beta(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:
    """Calculate portfolio beta relative to benchmark."""
    if portfolio_returns.empty or benchmark_returns.empty:
        return 0.0
    min_len = min(len(portfolio_returns), len(benchmark_returns))
    p = portfolio_returns.iloc[:min_len].values
    b = benchmark_returns.iloc[:min_len].values
    cov = np.cov(p, b)
    var_benchmark = cov[1, 1]
    if var_benchmark == 0:
        return 0.0
    return float(cov[0, 1] / var_benchmark)


def alpha(
    *,
    portfolio_return: float,
    benchmark_return: float,
    beta_value: float,
    risk_free_rate: float = 0.02,
) -> float:
    """Calculate Jensen's alpha."""
    return portfolio_return - (risk_free_rate + beta_value * (benchmark_return - risk_free_rate))
