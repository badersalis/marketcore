import logging
import time

import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.config import PUBLIC_ROUTES, is_public_product_route, settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter using Redis. Public routes: 100 req/min per IP.
    Authenticated routes: 300 req/min per user ID."""

    def __init__(self, app, redis: aioredis.Redis) -> None:
        super().__init__(app)
        self._redis = redis

    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        is_public = (method, path) in PUBLIC_ROUTES or is_public_product_route(method, path)

        if is_public:
            identifier = request.client.host if request.client else "unknown"
            limit = settings.RATE_LIMIT_PUBLIC
        else:
            identifier = getattr(request.state, "user_id", None) or request.client.host
            limit = settings.RATE_LIMIT_AUTHED

        key = f"rl:{identifier}:{int(time.time()) // 60}"
        try:
            count = await self._redis.incr(key)
            if count == 1:
                await self._redis.expire(key, 60)
            if count > limit:
                return JSONResponse(
                    {"detail": "Rate limit exceeded. Try again in a moment."},
                    status_code=429,
                    headers={"Retry-After": "60"},
                )
        except Exception as exc:
            logger.warning("Rate limiter Redis error — skipping: %s", exc)

        return await call_next(request)


__all__ = ["RateLimitMiddleware"]
