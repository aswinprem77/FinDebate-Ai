from typing import Literal

from pydantic import BaseModel

from app.schemas.debate import VerdictResponse
from app.schemas.evidence import EvidencePackage


class NewbieResult(BaseModel):
    action: Literal["Buy", "Hold", "Watch", "Avoid"]
    sentence: str
    latest_headline: str | None
    disclaimer: str


class IntermediateModelSummary(BaseModel):
    model: Literal["A", "B", "C"]
    role: str
    verdict: str
    confidence: str
    summary: str
    top_data_points: list[str]


class IntermediateIndicators(BaseModel):
    price: float
    daily_change_percent: float
    rsi: float | None
    macd_signal: str | None
    pe_ratio: float | None
    news_sentiment_score: float | None


class IntermediateResult(BaseModel):
    verdict: str
    confidence_band: str
    time_horizon: str
    action: str
    why: str
    indicators: IntermediateIndicators
    model_summaries: list[IntermediateModelSummary]
    disclaimer: str


class ProResult(BaseModel):
    verdict_response: VerdictResponse
    evidence_package: EvidencePackage
    export_ready: bool = True


class TierRenderedResult(BaseModel):
    ticker: str
    tier: Literal["newbie", "intermediate", "pro", "admin"]
    newbie: NewbieResult | None = None
    intermediate: IntermediateResult | None = None
    pro: ProResult | None = None
