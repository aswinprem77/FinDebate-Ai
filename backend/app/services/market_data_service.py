import re

from fastapi import HTTPException, status

from app.core.config import settings
from app.data.mock_market_data import build_mock_aapl_evidence
from app.schemas.evidence import EvidenceCacheInfo, EvidencePackage
from app.services.evidence_cache import evidence_cache

TICKER_PATTERN = re.compile(r"^[A-Z]{1,5}$")


class MarketDataService:
    async def get_evidence_package(self, ticker: str) -> EvidencePackage:
        normalized_ticker = ticker.strip().upper()
        if not TICKER_PATTERN.fullmatch(normalized_ticker):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ticker must be 1-5 letters for Module 2",
            )

        cache_key = f"market:evidence:{normalized_ticker}"
        cached = evidence_cache.get(cache_key)
        if cached:
            package = EvidencePackage.model_validate_json(cached)
            package.cache.status = "hit"
            package.cache.backend = evidence_cache.backend_name
            return package

        package = self._build_mock_evidence(normalized_ticker, cache_status="miss")
        evidence_cache.set(cache_key, package.model_dump_json(), settings.evidence_cache_ttl_seconds)
        return package

    def _build_mock_evidence(self, ticker: str, cache_status: str) -> EvidencePackage:
        cache_info = EvidenceCacheInfo(
            status=cache_status,
            backend=evidence_cache.backend_name,
            ttl_seconds=settings.evidence_cache_ttl_seconds,
        )

        if ticker == "AAPL":
            return build_mock_aapl_evidence(cache=cache_info)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module 2 currently includes mock evidence for AAPL only",
        )


market_data_service = MarketDataService()
