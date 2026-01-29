"""AI-powered portfolio insights using Claude API."""

from __future__ import annotations

import anthropic

from portfolio_ai.core.models import AnalysisResult

FALLBACK_MESSAGE = "AI 인사이트를 사용할 수 없습니다. --no-ai 옵션 없이 ANTHROPIC_API_KEY를 설정해주세요."

SYSTEM_PROMPT = (
    "당신은 전문 투자 포트폴리오 분석가입니다. "
    "주어진 포트폴리오 분석 데이터를 바탕으로 한국어로 인사이트를 제공하세요. "
    "간결하고 실행 가능한 조언을 포함해주세요."
)


def _build_prompt(result: AnalysisResult) -> str:
    holdings_text = "\n".join(
        f"  - {h.ticker} ({h.name}): 비중 {h.weight_pct:.1f}%, 수익률 {h.return_pct:.1f}%, 섹터: {h.sector}"
        for h in result.holdings_analysis
    )

    return f"""다음 포트폴리오 분석 결과를 바탕으로 투자 인사이트를 제공해주세요:

포트폴리오: {result.portfolio_name}
총 가치: {result.total_value:,.0f} {result.currency}
총 수익률: {result.total_return_pct:.2f}%
연환산 수익률: {result.annualized_return_pct:.2f}%
변동성: {result.volatility_pct:.2f}%
샤프 비율: {result.sharpe_ratio:.2f}
최대 낙폭: {result.max_drawdown_pct:.2f}%
베타: {result.beta:.2f}
알파: {result.alpha_pct:.2f}%
벤치마크: {result.benchmark_ticker}

보유 종목:
{holdings_text}

다음 항목을 분석해주세요:
1. 포트폴리오 강점과 약점
2. 섹터 집중도 리스크
3. 리스크 대비 수익 효율성
4. 개선 제안 (구체적인 액션 아이템)"""


def generate_insights(
    result: AnalysisResult,
    *,
    api_key: str | None = None,
) -> str:
    """Generate AI-powered insights for a portfolio analysis result."""
    if not api_key:
        return FALLBACK_MESSAGE

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": _build_prompt(result)},
            ],
        )
        return response.content[0].text
    except Exception:
        return FALLBACK_MESSAGE
