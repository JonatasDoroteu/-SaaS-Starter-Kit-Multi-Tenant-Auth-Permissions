from __future__ import annotations

import time

try:
    from redis.asyncio import Redis
except ImportError:  # Redis is optional for local/test execution.
    Redis = None  # type: ignore[assignment,misc]

from app.core.config import get_settings


class ApiKeyRateLimiter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._redis = None
        self._memory: dict[str, tuple[int, float]] = {}

    async def allow(self, key_hash: str) -> tuple[bool, int]:
        limit = self.settings.api_key_rate_limit
        window = self.settings.api_key_rate_window_seconds
        redis = await self._get_redis()
        if redis is not None:
            try:
                bucket = f"rate:api-key:{key_hash}:{int(time.time()) // window}"
                count = await redis.incr(bucket)
                if count == 1:
                    await redis.expire(bucket, window)
                return count <= limit, max(0, limit - count)
            except Exception:
                pass

        now = time.monotonic()
        count, started_at = self._memory.get(key_hash, (0, now))
        if now - started_at >= window:
            count, started_at = 0, now
        count += 1
        self._memory[key_hash] = (count, started_at)
        return count <= limit, max(0, limit - count)

    async def _get_redis(self) -> Redis | None:
        if Redis is None:
            return None
        if self._redis is None:
            self._redis = Redis.from_url(self.settings.redis_url, decode_responses=True)
        try:
            await self._redis.ping()
        except Exception:
            return None
        return self._redis


api_key_rate_limiter = ApiKeyRateLimiter()