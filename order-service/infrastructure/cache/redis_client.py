import redis.asyncio as aioredis

from core.config import settings


def create_redis_client() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


CART_TTL_AUTHENTICATED = 604_800  # 7 days for logged-in users
CART_TTL_GUEST = 86_400           # 24 h for guests

__all__ = ["create_redis_client", "CART_TTL_AUTHENTICATED", "CART_TTL_GUEST"]
