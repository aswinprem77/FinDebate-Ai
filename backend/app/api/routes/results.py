from fastapi import APIRouter, Depends

from app.api.deps_rate_limit import enforce_debate_rate_limit
from app.models.user import User
from app.schemas.tier_output import TierRenderedResult
from app.services.tier_renderer import tier_renderer
from app.services.verdict_engine import verdict_engine

router = APIRouter(prefix="/results", tags=["tier-results"])


@router.post("/{ticker}", response_model=TierRenderedResult)
async def run_tier_rendered_result(
    ticker: str,
    current_user: User = Depends(enforce_debate_rate_limit),
):
    verdict_response = await verdict_engine.run_verdict(ticker)
    return tier_renderer.render(verdict_response, current_user)
