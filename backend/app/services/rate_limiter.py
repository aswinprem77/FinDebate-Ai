from dataclasses import dataclass
from time import time

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.models.user import User, UserTier
from app.schemas.rate_limit import RateLimitQuota, RateLimitStatus


@dataclass(frozen=True)
class LimitPolicy:
    hourly: int | None
    daily: int | None
    warning_threshold_hourly: int | None = None


@dataclass(frozen=True)
class WindowResult:
    allowed: bool
    count: int
    limit: int | None
    remaining: int | None
    reset_seconds: int | None


class RateLimiter:
    backend_name = "memory"

    def check(self, *, user: User, route_key: str) -> RateLimitStatus:
        raise NotImplementedError


class SlidingWindowRateLimiter(RateLimiter):
    backend_name = "memory"

    def _policy_for(self, user: User) -> LimitPolicy:
        if user.rate_limit_override is not None:
            return LimitPolicy(hourly=user.rate_limit_override, daily=None)
        if user.tier == UserTier.ADMIN:
            return LimitPolicy(hourly=None, daily=None)
        if user.tier == UserTier.PRO:
            return LimitPolicy(
                hourly=settings.pro_debates_per_hour,
                daily=None,
                warning_threshold_hourly=settings.pro_warning_threshold_per_hour,
            )
        return LimitPolicy(hourly=settings.free_debates_per_hour, daily=settings.free_debates_per_day)

    def check(self, *, user: User, route_key: str) -> RateLimitStatus:
        policy = self._policy_for(user)
        if policy.hourly is None and policy.daily is None:
            return RateLimitStatus(
                allowed=True,
                backend=self.backend_name,
                tier=user.tier.value,
                hourly=RateLimitQuota(limit=None, remaining=None, reset_seconds=None),
                daily=RateLimitQuota(limit=None, remaining=None, reset_seconds=None),
            )

        now = time()
        hourly = self._check_window(
            key=f"rate:{user.user_id}:{route_key}:hour",
            now=now,
            window_seconds=60 * 60,
            limit=policy.hourly,
        )
        daily = self._check_window(
            key=f"rate:{user.user_id}:{route_key}:day",
            now=now,
            window_seconds=24 * 60 * 60,
            limit=policy.daily,
        )

        blocked_reason = None
        if not hourly.allowed:
            blocked_reason = "hourly"
        elif not daily.allowed:
            blocked_reason = "daily"

        warning = None
        if (
            policy.warning_threshold_hourly is not None
            and hourly.count >= policy.warning_threshold_hourly
            and hourly.allowed
        ):
            warning = f"Approaching hourly limit: {hourly.count}/{policy.hourly}"

        return RateLimitStatus(
            allowed=blocked_reason is None,
            backend=self.backend_name,
            tier=user.tier.value,
            hourly=RateLimitQuota(
                limit=hourly.limit,
                remaining=hourly.remaining,
                reset_seconds=hourly.reset_seconds,
            ),
            daily=RateLimitQuota(
                limit=daily.limit,
                remaining=daily.remaining,
                reset_seconds=daily.reset_seconds,
            ),
            warning=warning,
            blocked_reason=blocked_reason,
        )

    def _check_window(
        self,
        *,
        key: str,
        now: float,
        window_seconds: int,
        limit: int | None,
    ) -> WindowResult:
        raise NotImplementedError


class MemoryRateLimiter(SlidingWindowRateLimiter):
    backend_name = "memory"

    def __init__(self) -> None:
        self._events: dict[str, list[float]] = {}

    def _check_window(
        self,
        *,
        key: str,
        now: float,
        window_seconds: int,
        limit: int | None,
    ) -> WindowResult:
        if limit is None:
            return WindowResult(True, 0, None, None, None)

        cutoff = now - window_seconds
        events = [event for event in self._events.get(key, []) if event > cutoff]
        allowed = len(events) < limit
        if allowed:
            events.append(now)
        self._events[key] = events

        reset_seconds = max(1, int(events[0] + window_seconds - now)) if events else window_seconds
        remaining = max(0, limit - len(events))
        return WindowResult(allowed, len(events), limit, remaining, reset_seconds)


class RedisRateLimiter(SlidingWindowRateLimiter):
    backend_name = "redis"

    def __init__(self, redis_url: str) -> None:
        self._client = Redis.from_url(redis_url, decode_responses=True)

    def _check_window(
        self,
        *,
        key: str,
        now: float,
        window_seconds: int,
        limit: int | None,
    ) -> WindowResult:
        if limit is None:
            return WindowResult(True, 0, None, None, None)

        member = f"{now}"
        cutoff = now - window_seconds
        pipe = self._client.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zcard(key)
        _, count_before = pipe.execute()

        allowed = int(count_before) < limit
        if allowed:
            pipe = self._client.pipeline()
            pipe.zadd(key, {member: now})
            pipe.expire(key, window_seconds)
            pipe.zcard(key)
            _, _, count = pipe.execute()
        else:
            count = int(count_before)

        oldest = self._client.zrange(key, 0, 0, withscores=True)
        reset_seconds = window_seconds
        if oldest:
            reset_seconds = max(1, int(oldest[0][1] + window_seconds - now))

        remaining = max(0, limit - int(count))
        return WindowResult(allowed, int(count), limit, remaining, reset_seconds)


def build_rate_limiter() -> RateLimiter:
    if not settings.redis_url:
        return MemoryRateLimiter()

    try:
        limiter = RedisRateLimiter(settings.redis_url)
        limiter._client.ping()
        return limiter
    except RedisError:
        return MemoryRateLimiter()


rate_limiter = build_rate_limiter()
