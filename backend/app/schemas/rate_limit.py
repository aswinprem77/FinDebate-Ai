from typing import Literal

from pydantic import BaseModel


class RateLimitQuota(BaseModel):
    limit: int | None
    remaining: int | None
    reset_seconds: int | None


class RateLimitStatus(BaseModel):
    allowed: bool
    backend: Literal["redis", "memory"]
    tier: str
    hourly: RateLimitQuota
    daily: RateLimitQuota
    warning: str | None = None
    blocked_reason: str | None = None
