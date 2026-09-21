from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.security import hash_api_key
from app.db import AsyncSessionLocal
from app.models.api_key import ApiKey
from app.services.rate_limit import api_key_rate_limiter


class ApiKeyRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw_key = request.headers.get("X-API-Key")
        if not raw_key:
            return await call_next(request)

        key_hash = hash_api_key(raw_key)
        async with AsyncSessionLocal() as session:
            if session.bind.dialect.name == "postgresql":
                await session.execute(
                    text("SELECT set_config('app.api_key_hash', :key_hash, true)"),
                    {"key_hash": key_hash},
                )
            api_key = await session.scalar(select(ApiKey).where(ApiKey.hashed_key == key_hash))
            if api_key is None or api_key.revoked_at is not None:
                return JSONResponse(status_code=401, content={"detail": "Invalid or revoked API key"})

        settings = get_settings()
        allowed, remaining = await api_key_rate_limiter.allow(key_hash)
        headers = {
            "X-RateLimit-Limit": str(settings.api_key_rate_limit),
            "X-RateLimit-Remaining": str(remaining),
        }
        if not allowed:
            headers["Retry-After"] = str(settings.api_key_rate_window_seconds)
            return JSONResponse(status_code=429, content={"detail": "API key rate limit exceeded"}, headers=headers)

        response = await call_next(request)
        response.headers.update(headers)
        return response