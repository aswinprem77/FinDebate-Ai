from app.models.user import User, UserTier
from app.schemas.debate import AnalystOutput, VerdictResponse
from app.schemas.tier_output import (
    IntermediateIndicators,
    IntermediateModelSummary,
    IntermediateResult,
    NewbieResult,
    ProResult,
    TierRenderedResult,
)


class TierRenderer:
    def render(self, verdict_response: VerdictResponse, user: User) -> TierRenderedResult:
        if user.tier == UserTier.PRO or user.tier == UserTier.ADMIN:
            return self._render_pro(verdict_response, user)
        if user.tier == UserTier.INTERMEDIATE:
            return self._render_intermediate(verdict_response, user)
        return self._render_newbie(verdict_response, user)

    def _render_newbie(self, verdict_response: VerdictResponse, user: User) -> TierRenderedResult:
        judge = verdict_response.judge_verdict
        evidence = verdict_response.debate.evidence_package
        headline = None
        if evidence.news_sentiment and evidence.news_sentiment.headlines:
            headline = evidence.news_sentiment.headlines[0].headline

        return TierRenderedResult(
            ticker=verdict_response.metadata.ticker,
            tier=user.tier.value,
            newbie=NewbieResult(
                action=judge.action_suggestion,
                sentence=self._newbie_sentence(verdict_response),
                latest_headline=headline,
                disclaimer=judge.disclaimer,
            ),
        )

    def _render_intermediate(self, verdict_response: VerdictResponse, user: User) -> TierRenderedResult:
        judge = verdict_response.judge_verdict
        evidence = verdict_response.debate.evidence_package
        technicals = evidence.technicals
        fundamentals = evidence.fundamentals
        news = evidence.news_sentiment

        return TierRenderedResult(
            ticker=verdict_response.metadata.ticker,
            tier=user.tier.value,
            intermediate=IntermediateResult(
                verdict=judge.verdict,
                confidence_band=judge.confidence_band,
                time_horizon=judge.time_horizon,
                action=judge.action_suggestion,
                why=judge.why_winner_won,
                indicators=IntermediateIndicators(
                    price=evidence.price_volume.current_price,
                    daily_change_percent=evidence.price_volume.daily_change_percent,
                    rsi=technicals.rsi if technicals else None,
                    macd_signal=technicals.macd_signal if technicals else None,
                    pe_ratio=fundamentals.pe_ratio if fundamentals else None,
                    news_sentiment_score=news.aggregate_score if news else None,
                ),
                model_summaries=[
                    self._model_summary(verdict_response.debate.model_a_output),
                    self._model_summary(verdict_response.debate.model_b_output),
                    self._model_summary(verdict_response.debate.model_c_output),
                ],
                disclaimer=judge.disclaimer,
            ),
        )

    def _render_pro(self, verdict_response: VerdictResponse, user: User) -> TierRenderedResult:
        return TierRenderedResult(
            ticker=verdict_response.metadata.ticker,
            tier=user.tier.value,
            pro=ProResult(
                verdict_response=verdict_response,
                evidence_package=verdict_response.debate.evidence_package,
            ),
        )

    def _newbie_sentence(self, verdict_response: VerdictResponse) -> str:
        ticker = verdict_response.metadata.ticker
        action = verdict_response.judge_verdict.action_suggestion
        verdict = verdict_response.judge_verdict.verdict
        if verdict == "Bullish":
            return f"{ticker} looks positive overall, so the current suggestion is {action.lower()}."
        if verdict == "Bearish":
            return f"{ticker} looks risky right now, so the current suggestion is {action.lower()}."
        return f"{ticker} is not giving a clear signal yet, so the current suggestion is {action.lower()}."

    def _model_summary(self, output: AnalystOutput) -> IntermediateModelSummary:
        return IntermediateModelSummary(
            model=output.model_label,
            role=output.role.replace("_", " "),
            verdict=output.verdict,
            confidence=output.confidence,
            summary=output.plain_english_summary,
            top_data_points=output.top_3_data_points,
        )


tier_renderer = TierRenderer()
