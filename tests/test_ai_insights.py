"""Tests for AI insights generation."""

from unittest.mock import MagicMock, patch

import pytest

from portfolio_ai.core.ai_insights import generate_insights
from portfolio_ai.core.models import AnalysisResult, HoldingAnalysis


@pytest.fixture
def sample_result():
    holdings = (
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
    return AnalysisResult(
        portfolio_name="Test Portfolio",
        total_value=3500.0,
        total_cost=3000.0,
        total_return_pct=16.67,
        annualized_return_pct=16.67,
        volatility_pct=20.0,
        sharpe_ratio=0.73,
        max_drawdown_pct=-8.0,
        beta=1.1,
        alpha_pct=2.0,
        currency="USD",
        holdings_analysis=holdings,
        benchmark_ticker="SPY",
    )


class TestGenerateInsights:
    @patch("portfolio_ai.core.ai_insights.anthropic")
    def test_returns_string(self, mock_anthropic, sample_result):
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="포트폴리오 분석 결과입니다.")]
        mock_client.messages.create.return_value = mock_response

        result = generate_insights(sample_result, api_key="test-key")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("portfolio_ai.core.ai_insights.anthropic")
    def test_calls_api_with_korean_prompt(self, mock_anthropic, sample_result):
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="분석 결과")]
        mock_client.messages.create.return_value = mock_response

        generate_insights(sample_result, api_key="test-key")

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs.get("messages") or call_args[1].get("messages")
        user_msg = messages[0]["content"]
        assert "포트폴리오" in user_msg or "portfolio" in user_msg.lower()

    @patch("portfolio_ai.core.ai_insights.anthropic")
    def test_api_failure_returns_fallback(self, mock_anthropic, sample_result):
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        result = generate_insights(sample_result, api_key="test-key")
        assert result is not None
        assert "사용할 수 없습니다" in result or "unavailable" in result.lower()

    def test_no_api_key_returns_fallback(self, sample_result):
        result = generate_insights(sample_result, api_key=None)
        assert result is not None
        assert "사용할 수 없습니다" in result or "unavailable" in result.lower()
