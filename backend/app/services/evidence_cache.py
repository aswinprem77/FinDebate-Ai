from time import monotonic

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


class EvidenceCache:
    backend_name = "memory"

    def get(self, key: str) -> str | None:
        raise NotImplementedError

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        raise NotImplementedError


class MemoryEvidenceCache(EvidenceCache):
    backend_name = "memory"

    def __init__(self) -> None:
        self._items: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> str | None:
        item = self._items.get(key)
        if item is None:
            return None

        expires_at, value = item
        if expires_at <= monotonic():
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._items[key] = (monotonic() + ttl_seconds, value)


class RedisEvidenceCache(EvidenceCache):
    backend_name = "redis"

    def __init__(self, redis_url: str) -> None:
        self._client = Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._client.setex(key, ttl_seconds, value)


def build_evidence_cache() -> EvidenceCache:
    if not settings.redis_url:
        return MemoryEvidenceCache()

    try:
        cache = RedisEvidenceCache(settings.redis_url)
        cache._client.ping()
        return cache
    except RedisError:
        return MemoryEvidenceCache()


evidence_cache = build_evidence_cache()
