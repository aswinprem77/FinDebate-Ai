from fastapi import Depends, HTTPException, Request, Response, status

from app.api.deps import get_current_user
from app.models.user import User
from app.services.rate_limit_logger import rate_limit_logger
from app.services.rate_limiter import rate_limiter


async def enforce_debate_rate_limit(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
) -> User:
    result = rate_limiter.check(user=current_user, route_key="debate")

    if result.hourly.limit is not None:
        response.headers["X-RateLimit-Hour-Limit"] = str(result.hourly.limit)
        response.headers["X-RateLimit-Hour-Remaining"] = str(result.hourly.remaining)
        response.headers["X-RateLimit-Hour-Reset"] = str(result.hourly.reset_seconds)
    if result.daily.limit is not None:
        response.headers["X-RateLimit-Day-Limit"] = str(result.daily.limit)
        response.headers["X-RateLimit-Day-Remaining"] = str(result.daily.remaining)
        response.headers["X-RateLimit-Day-Reset"] = str(result.daily.reset_seconds)
    response.headers["X-RateLimit-Backend"] = result.backend

    if result.allowed:
        return current_user

    blocked_quota = result.hourly if result.blocked_reason == "hourly" else result.daily
    headers = {"X-RateLimit-Backend": result.backend}
    if result.hourly.limit is not None:
        headers["X-RateLimit-Hour-Limit"] = str(result.hourly.limit)
        headers["X-RateLimit-Hour-Remaining"] = str(result.hourly.remaining)
        headers["X-RateLimit-Hour-Reset"] = str(result.hourly.reset_seconds)
    if result.daily.limit is not None:
        headers["X-RateLimit-Day-Limit"] = str(result.daily.limit)
        headers["X-RateLimit-Day-Remaining"] = str(result.daily.remaining)
        headers["X-RateLimit-Day-Reset"] = str(result.daily.reset_seconds)

    rate_limit_logger.log_block(
        user=current_user,
        route=str(request.url.path),
        limit_type=result.blocked_reason or "unknown",
        limit_value=blocked_quota.limit or 0,
        observed_count=(blocked_quota.limit or 0) + 1,
    )
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "message": "Rate limit exceeded",
            "rate_limit": result.model_dump(),
        },
        headers=headers,
    )
