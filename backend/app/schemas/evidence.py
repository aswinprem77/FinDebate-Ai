from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Sentiment = Literal["positive", "negative", "neutral"]


class PriceVolumeEvidence(BaseModel):
    current_price: float
    daily_change_percent: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    average_volume: int
    five_day_direction: Literal["up", "down", "flat"]
    twenty_day_direction: Literal["up", "down", "flat"]


class TechnicalEvidence(BaseModel):
    rsi: float
    macd_signal: Literal["bullish", "bearish", "neutral"]
    ma_50: float
    ma_200: float
    bollinger_position: Literal["upper", "middle", "lower"]
    atr: float
    stochastic: float


class FundamentalEvidence(BaseModel):
    pe_ratio: float
    eps: float
    revenue_growth_percent: float
    debt_to_equity: float
    free_cash_flow_billions: float
    roe_percent: float
    next_earnings_date: str
    analyst_consensus: Literal["buy", "hold", "sell"]


class NewsItem(BaseModel):
    headline: str
    source: str
    sentiment: Sentiment
    sentiment_score: float = Field(ge=-1, le=1)
    published_at: str


class NewsSentimentEvidence(BaseModel):
    aggregate_sentiment: Sentiment
    aggregate_score: float = Field(ge=-1, le=1)
    headlines: list[NewsItem]


class EvidenceWarnings(BaseModel):
    missing_categories: list[str] = Field(default_factory=list)
    provider_errors: list[str] = Field(default_factory=list)


class EvidenceCacheInfo(BaseModel):
    status: Literal["hit", "miss", "disabled"]
    backend: Literal["redis", "memory"]
    ttl_seconds: int


class EvidencePackage(BaseModel):
    ticker: str
    as_of: datetime
    source_mode: Literal["mock", "live"]
    price_volume: PriceVolumeEvidence
    technicals: TechnicalEvidence | None = None
    fundamentals: FundamentalEvidence | None = None
    news_sentiment: NewsSentimentEvidence | None = None
    warnings: EvidenceWarnings = Field(default_factory=EvidenceWarnings)
    cache: EvidenceCacheInfo
