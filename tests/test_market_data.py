"""Tests for market data (yfinance wrapper)."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from portfolio_ai.data.market_data import MarketDataProvider


@pytest.fixture
def provider():
    return MarketDataProvider()


@pytest.fixture
def mock_ticker():
    """Create a mocked yfinance Ticker."""
    ticker = MagicMock()
    ticker.info = {
        "currentPrice": 175.0,
        "sector": "Technology",
        "shortName": "Apple Inc.",
    }
    dates = pd.date_range(end=date.today(), periods=252, freq="B")
    ticker.history.return_value = pd.DataFrame(
        {"Close": [150.0 + i * 0.1 for i in range(252)]},
        index=dates,
    )
    return ticker


class TestMarketDataProvider:
    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_current_price(self, mock_yf_ticker, provider, mock_ticker):
        mock_yf_ticker.return_value = mock_ticker
        price = provider.get_current_price("AAPL")
        assert price == 175.0

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_current_price_fallback_to_close(self, mock_yf_ticker, provider):
        ticker = MagicMock()
        ticker.info = {}
        dates = pd.date_range(end=date.today(), periods=5, freq="B")
        ticker.history.return_value = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0, 103.0, 104.0]},
            index=dates,
        )
        mock_yf_ticker.return_value = ticker
        price = provider.get_current_price("AAPL")
        assert price == 104.0

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_current_price_failure(self, mock_yf_ticker, provider):
        ticker = MagicMock()
        ticker.info = {}
        ticker.history.return_value = pd.DataFrame()
        mock_yf_ticker.return_value = ticker
        price = provider.get_current_price("INVALID")
        assert price is None

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_sector(self, mock_yf_ticker, provider, mock_ticker):
        mock_yf_ticker.return_value = mock_ticker
        sector = provider.get_sector("AAPL")
        assert sector == "Technology"

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_sector_unknown(self, mock_yf_ticker, provider):
        ticker = MagicMock()
        ticker.info = {}
        mock_yf_ticker.return_value = ticker
        sector = provider.get_sector("UNKNOWN")
        assert sector == "Unknown"

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_historical_prices(self, mock_yf_ticker, provider, mock_ticker):
        mock_yf_ticker.return_value = mock_ticker
        prices = provider.get_historical_prices("AAPL", period="1y")
        assert isinstance(prices, pd.Series)
        assert len(prices) == 252

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_get_historical_prices_empty(self, mock_yf_ticker, provider):
        ticker = MagicMock()
        ticker.history.return_value = pd.DataFrame()
        mock_yf_ticker.return_value = ticker
        prices = provider.get_historical_prices("INVALID", period="1y")
        assert prices.empty

    @patch("portfolio_ai.data.market_data.yf.Ticker")
    def test_caching(self, mock_yf_ticker, provider, mock_ticker):
        mock_yf_ticker.return_value = mock_ticker
        provider.get_current_price("AAPL")
        provider.get_current_price("AAPL")
        assert mock_yf_ticker.call_count == 1
