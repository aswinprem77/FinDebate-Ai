import asyncio
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.debate import AnalystOutput, DebateResponse, JudgeVerdict, VerdictMetadata, VerdictResponse
from app.services.debate_engine import debate_engine

DISCLAIMER = "This is AI-generated analysis for educational purposes only. This is not financial advice."


class MockJudgeModel:
    async def judge(self, debate: DebateResponse) -> JudgeVerdict:
        await asyncio.sleep(0)
        outputs = [
            debate.model_a_output,
            debate.model_b_output,
            debate.model_c_output,
        ]
        winner = self._select_winner(outputs)
        verdict = self._consensus_verdict(outputs, winner)

        return JudgeVerdict(
            provider_model="mock-gpt-4o-judge",
            winning_model=winner.model_label,
            verdict=verdict,
            confidence_band=self._confidence_band(outputs, verdict),
            why_winner_won=(
                f"Model {winner.model_label} presented the most coherent case because its conclusion follows "
                "directly from its stated evidence and includes a clear risk that could invalidate the thesis."
            ),
            minority_view=self._minority_view(outputs, winner),
            time_horizon=self._time_horizon(winner),
            action_suggestion=self._action_suggestion(verdict),
            disclaimer=DISCLAIMER,
        )

    def fallback(self, error: str, debate: DebateResponse) -> JudgeVerdict:
        return JudgeVerdict(
            provider_model="mock-judge-fallback",
            winning_model="tie",
            verdict="Neutral",
            confidence_band="Weak",
            why_winner_won="The judge could not complete a reliable evaluation.",
            minority_view="All model outputs should be reviewed manually before relying on the result.",
            time_horizon="1 month",
            action_suggestion="Watch",
            disclaimer=DISCLAIMER,
            is_fallback=True,
            error=error,
        )

    def _select_winner(self, outputs: list[AnalystOutput]) -> AnalystOutput:
        confidence_score = {"High": 3, "Medium": 2, "Low": 1}
        role_priority = {"technical": 0, "fundamental": 1, "macro_sentiment": 2}
        return max(
            outputs,
            key=lambda output: (
                not output.is_fallback,
                confidence_score[output.confidence],
                len(output.full_reasoning),
                role_priority[output.role],
            ),
        )

    def _consensus_verdict(self, outputs: list[AnalystOutput], winner: AnalystOutput) -> str:
        counts = {verdict: 0 for verdict in ["Bullish", "Bearish", "Neutral"]}
        for output in outputs:
            if not output.is_fallback:
                counts[output.verdict] += 1

        top_verdict, top_count = max(counts.items(), key=lambda item: item[1])
        if top_count >= 2:
            return top_verdict
        return winner.verdict

    def _confidence_band(self, outputs: list[AnalystOutput], verdict: str) -> str:
        agreeing = [output for output in outputs if output.verdict == verdict and not output.is_fallback]
        if len(agreeing) == 3 and all(output.confidence in {"High", "Medium"} for output in agreeing):
            return "Strong"
        if len(agreeing) >= 2:
            return "Moderate"
        return "Weak"

    def _minority_view(self, outputs: list[AnalystOutput], winner: AnalystOutput) -> str:
        minority = [output for output in outputs if output.model_label != winner.model_label]
        useful_points = [output.risk_to_thesis for output in minority if not output.is_fallback]
        if not useful_points:
            return "No strong minority view was available because one or more models used fallback output."
        return " ".join(useful_points[:2])

    def _time_horizon(self, winner: AnalystOutput) -> str:
        if winner.role == "technical":
            return "1 week"
        if winner.role == "macro_sentiment":
            return "1 month"
        return "3 months"

    def _action_suggestion(self, verdict: str) -> str:
        if verdict == "Bullish":
            return "Buy"
        if verdict == "Bearish":
            return "Avoid"
        return "Watch"


class VerdictEngine:
    def __init__(self, judge_model: MockJudgeModel) -> None:
        self._judge_model = judge_model

    async def run_verdict(self, ticker: str) -> VerdictResponse:
        debate = await debate_engine.run_debate(ticker)
        judge = await self._judge_with_timeout(debate)
        return VerdictResponse(
            metadata=VerdictMetadata(
                ticker=debate.metadata.ticker,
                generated_at=datetime.now(timezone.utc),
                judge_timeout_seconds=settings.judge_timeout_seconds,
                partial=debate.metadata.partial or judge.is_fallback,
            ),
            debate=debate,
            judge_verdict=judge,
        )

    async def _judge_with_timeout(self, debate: DebateResponse) -> JudgeVerdict:
        try:
            return await asyncio.wait_for(
                self._judge_model.judge(debate),
                timeout=settings.judge_timeout_seconds,
            )
        except Exception as exc:
            return self._judge_model.fallback(str(exc), debate)


verdict_engine = VerdictEngine(judge_model=MockJudgeModel())
