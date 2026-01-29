"""Market data provider using yfinance."""

from __future__ import annotations

import yfinance as yf
import pandas as pd


class MarketDataProvider:
    """Wrapper around yfinance for market data retrieval."""

    def __init__(self) -> None:
        self._cache: dict[str, yf.Ticker] = {}

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        if symbol not in self._cache:
            self._cache[symbol] = yf.Ticker(symbol)
        return self._cache[symbol]

    def get_current_price(self, symbol: str) -> float | None:
        """Get the current price for a symbol."""
        try:
            ticker = self._get_ticker(symbol)
            info = ticker.info
            price = info.get("currentPrice")
            if price is not None:
                return float(price)

            hist = ticker.history(period="5d")
            if not hist.empty:
                return float(hist["Close"].iloc[-1])
        except Exception:
            pass
        return None

    def get_sector(self, symbol: str) -> str:
        """Get the sector for a symbol."""
        try:
            ticker = self._get_ticker(symbol)
            return ticker.info.get("sector", "Unknown")
        except Exception:
            return "Unknown"

    def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
    ) -> pd.Series:
        """Get historical closing prices for a symbol."""
        try:
            ticker = self._get_ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return pd.Series(dtype=float)
            return hist["Close"]
        except Exception:
            return pd.Series(dtype=float)
