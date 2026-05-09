from fastapi import APIRouter, Depends

from app.api.deps_rate_limit import enforce_debate_rate_limit
from app.schemas.debate import VerdictResponse
from app.services.verdict_engine import verdict_engine

router = APIRouter(prefix="/verdict", tags=["verdict"])


@router.post("/{ticker}", response_model=VerdictResponse)
async def run_verdict(ticker: str, _current_user=Depends(enforce_debate_rate_limit)):
    return await verdict_engine.run_verdict(ticker)
