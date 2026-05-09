from fastapi import APIRouter, Depends

from app.api.deps_rate_limit import enforce_debate_rate_limit
from app.schemas.debate import DebateResponse
from app.services.debate_engine import debate_engine

router = APIRouter(prefix="/debate", tags=["debate"])


@router.post("/{ticker}", response_model=DebateResponse)
async def run_debate(ticker: str, _current_user=Depends(enforce_debate_rate_limit)):
    return await debate_engine.run_debate(ticker)
