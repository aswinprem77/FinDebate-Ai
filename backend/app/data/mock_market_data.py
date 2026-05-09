from datetime import datetime, timezone

from app.schemas.evidence import (
    EvidenceCacheInfo,
    EvidencePackage,
    FundamentalEvidence,
    NewsItem,
    NewsSentimentEvidence,
    PriceVolumeEvidence,
    TechnicalEvidence,
)


def build_mock_aapl_evidence(cache: EvidenceCacheInfo) -> EvidencePackage:
    return EvidencePackage(
        ticker="AAPL",
        as_of=datetime.now(timezone.utc),
        source_mode="mock",
        price_volume=PriceVolumeEvidence(
            current_price=204.73,
            daily_change_percent=0.84,
            fifty_two_week_high=237.49,
            fifty_two_week_low=164.08,
            average_volume=58_300_000,
            five_day_direction="up",
            twenty_day_direction="flat",
        ),
        technicals=TechnicalEvidence(
            rsi=57.2,
            macd_signal="bullish",
            ma_50=198.45,
            ma_200=191.12,
            bollinger_position="middle",
            atr=3.91,
            stochastic=61.8,
        ),
        fundamentals=FundamentalEvidence(
            pe_ratio=31.4,
            eps=6.52,
            revenue_growth_percent=2.1,
            debt_to_equity=1.47,
            free_cash_flow_billions=99.6,
            roe_percent=154.3,
            next_earnings_date="2026-07-30",
            analyst_consensus="buy",
        ),
        news_sentiment=NewsSentimentEvidence(
            aggregate_sentiment="positive",
            aggregate_score=0.38,
            headlines=[
                NewsItem(
                    headline="Apple supplier checks point to steady iPhone demand",
                    source="MockWire",
                    sentiment="positive",
                    sentiment_score=0.42,
                    published_at="2026-05-10",
                ),
                NewsItem(
                    headline="Services revenue remains a focus for investors",
                    source="Mock Markets",
                    sentiment="neutral",
                    sentiment_score=0.08,
                    published_at="2026-05-09",
                ),
            ],
        ),
        cache=cache,
    )
