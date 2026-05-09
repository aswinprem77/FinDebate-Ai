from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.evidence import EvidencePackage

ModelRole = Literal["fundamental", "technical", "macro_sentiment"]
ModelLabel = Literal["A", "B", "C"]
Verdict = Literal["Bullish", "Bearish", "Neutral"]
Confidence = Literal["High", "Medium", "Low"]


class AnalystOutput(BaseModel):
    model_label: ModelLabel
    role: ModelRole
    provider_model: str
    verdict: Verdict
    confidence: Confidence
    top_3_data_points: list[str] = Field(min_length=3, max_length=3)
    key_assumption: str
    risk_to_thesis: str
    plain_english_summary: str
    full_reasoning: str
    is_fallback: bool = False
    error: str | None = None


class DebateRunMetadata(BaseModel):
    ticker: str
    generated_at: datetime
    evidence_source_mode: Literal["mock", "live"]
    evidence_cache_status: str
    model_timeout_seconds: int
    partial: bool


class DebateResponse(BaseModel):
    metadata: DebateRunMetadata
    evidence_package: EvidencePackage
    model_a_output: AnalystOutput
    model_b_output: AnalystOutput
    model_c_output: AnalystOutput
