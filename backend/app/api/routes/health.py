from fastapi import APIRouter

from app.core.feature_flags import feature_flags
from app.services.evidence_cache import evidence_cache
from app.services.rate_limiter import rate_limiter
from app.services.user_store import user_store

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "module": "M4_THREE_MODEL_DEBATE_ENGINE",
        "user_store": user_store.backend_name,
        "evidence_cache": evidence_cache.backend_name,
        "rate_limiter": rate_limiter.backend_name,
        "feature_flags": feature_flags.model_dump(),
    }
