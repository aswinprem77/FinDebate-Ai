from fastapi import APIRouter, Depends

from app.api.deps_rate_limit import enforce_debate_rate_limit
from app.schemas.evidence import EvidencePackage
from app.services.market_data_service import market_data_service

router = APIRouter(prefix="/market", tags=["market-data"])


@router.get("/evidence/{ticker}", response_model=EvidencePackage)
async def get_evidence_package(ticker: str, _current_user=Depends(enforce_debate_rate_limit)):
    return await market_data_service.get_evidence_package(ticker)
