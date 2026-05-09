import asyncio
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.debate import AnalystOutput, DebateResponse, DebateRunMetadata
from app.schemas.evidence import EvidencePackage
from app.services.market_data_service import market_data_service


class MockAnalystModel:
    async def run_fundamental(self, evidence: EvidencePackage) -> AnalystOutput:
        await asyncio.sleep(0)
        fundamentals = evidence.fundamentals
        price = evidence.price_volume
        if fundamentals is None:
            return self._fallback("A", "fundamental", "Missing fundamental evidence")

        verdict = "Bullish" if fundamentals.free_cash_flow_billions > 50 else "Neutral"
        confidence = "Medium" if fundamentals.pe_ratio > 30 else "High"
        return AnalystOutput(
            model_label="A",
            role="fundamental",
            provider_model="mock-gpt-4o-fundamental",
            verdict=verdict,
            confidence=confidence,
            top_3_data_points=[
                f"Free cash flow is ${fundamentals.free_cash_flow_billions}B",
                f"P/E ratio is {fundamentals.pe_ratio}",
                f"Analyst consensus is {fundamentals.analyst_consensus}",
            ],
            key_assumption="Apple's cash generation can continue supporting premium valuation.",
            risk_to_thesis="A sharper revenue slowdown or margin pressure would weaken the valuation case.",
            plain_english_summary=f"{evidence.ticker} looks financially strong, but the stock is not cheap.",
            full_reasoning=(
                f"{evidence.ticker} has strong free cash flow and high return on equity, which supports a constructive "
                f"view. The main constraint is valuation: a P/E near {fundamentals.pe_ratio} leaves less room for "
                f"disappointment. Current price action around ${price.current_price} does not change the fundamental case."
            ),
        )

    async def run_technical(self, evidence: EvidencePackage) -> AnalystOutput:
        await asyncio.sleep(0)
        technicals = evidence.technicals
        price = evidence.price_volume
        if technicals is None:
            return self._fallback("B", "technical", "Missing technical evidence")

        verdict = "Bullish" if technicals.macd_signal == "bullish" and price.five_day_direction == "up" else "Neutral"
        confidence = "Medium" if 45 <= technicals.rsi <= 65 else "Low"
        return AnalystOutput(
            model_label="B",
            role="technical",
            provider_model="mock-claude-sonnet-technical",
            verdict=verdict,
            confidence=confidence,
            top_3_data_points=[
                f"RSI is {technicals.rsi}",
                f"MACD signal is {technicals.macd_signal}",
                f"50-day average is {technicals.ma_50} versus 200-day average {technicals.ma_200}",
            ],
            key_assumption="Recent upward momentum can continue while price remains above key moving averages.",
            risk_to_thesis="A close below the 50-day moving average would weaken the momentum setup.",
            plain_english_summary=f"{evidence.ticker} has a mildly positive chart setup without looking overheated.",
            full_reasoning=(
                f"The technical picture is constructive: RSI at {technicals.rsi} is not extreme, MACD is "
                f"{technicals.macd_signal}, and the 50-day average is above the 200-day average. ATR of "
                f"{technicals.atr} suggests normal movement risk rather than an immediate volatility break."
            ),
        )

    async def run_macro_sentiment(self, evidence: EvidencePackage) -> AnalystOutput:
        await asyncio.sleep(0)
        sentiment = evidence.news_sentiment
        if sentiment is None:
            return self._fallback("C", "macro_sentiment", "Missing news sentiment evidence")

        verdict = "Bullish" if sentiment.aggregate_score > 0.25 else "Neutral"
        confidence = "Low" if len(sentiment.headlines) < 3 else "Medium"
        return AnalystOutput(
            model_label="C",
            role="macro_sentiment",
            provider_model="mock-gemini-macro-sentiment",
            verdict=verdict,
            confidence=confidence,
            top_3_data_points=[
                f"Aggregate sentiment is {sentiment.aggregate_sentiment}",
                f"Sentiment score is {sentiment.aggregate_score}",
                f"Latest headline: {sentiment.headlines[0].headline}",
            ],
            key_assumption="Recent headlines reflect a stable investor backdrop for the stock.",
            risk_to_thesis="A negative product-cycle headline or broader market risk-off move could reverse sentiment.",
            plain_english_summary=f"Recent news around {evidence.ticker} is slightly supportive, but not decisive.",
            full_reasoning=(
                f"News sentiment is {sentiment.aggregate_sentiment} with a score of {sentiment.aggregate_score}. "
                "The available mock headlines point to steady demand and services focus, which supports a mild "
                "positive stance, though the evidence set is still thin."
            ),
        )

    def _fallback(self, model_label: str, role: str, error: str) -> AnalystOutput:
        return AnalystOutput(
            model_label=model_label,
            role=role,
            provider_model="mock-fallback",
            verdict="Neutral",
            confidence="Low",
            top_3_data_points=["Missing evidence", "Model fallback", "Manual review needed"],
            key_assumption="Insufficient evidence is safer than forcing a directional view.",
            risk_to_thesis="The missing data may contain decisive bullish or bearish signals.",
            plain_english_summary="There is not enough information for this model to take a strong view.",
            full_reasoning="The model returned a fallback output because its required evidence was unavailable.",
            is_fallback=True,
            error=error,
        )


class DebateEngine:
    def __init__(self, analyst_model: MockAnalystModel) -> None:
        self._analyst_model = analyst_model

    async def run_debate(self, ticker: str) -> DebateResponse:
        evidence = await market_data_service.get_evidence_package(ticker)
        outputs = await asyncio.gather(
            self._with_timeout(self._analyst_model.run_fundamental(evidence), "A", "fundamental"),
            self._with_timeout(self._analyst_model.run_technical(evidence), "B", "technical"),
            self._with_timeout(self._analyst_model.run_macro_sentiment(evidence), "C", "macro_sentiment"),
        )

        partial = any(output.is_fallback for output in outputs)
        return DebateResponse(
            metadata=DebateRunMetadata(
                ticker=evidence.ticker,
                generated_at=datetime.now(timezone.utc),
                evidence_source_mode=evidence.source_mode,
                evidence_cache_status=evidence.cache.status,
                model_timeout_seconds=settings.model_timeout_seconds,
                partial=partial,
            ),
            evidence_package=evidence,
            model_a_output=outputs[0],
            model_b_output=outputs[1],
            model_c_output=outputs[2],
        )

    async def _with_timeout(self, task, model_label: str, role: str) -> AnalystOutput:
        try:
            return await asyncio.wait_for(task, timeout=settings.model_timeout_seconds)
        except Exception as exc:
            return self._analyst_model._fallback(model_label, role, str(exc))


debate_engine = DebateEngine(analyst_model=MockAnalystModel())
