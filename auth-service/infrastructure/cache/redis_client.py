from redis.asyncio import Redis

from core.config import settings


def create_redis_client() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


__all__ = ["create_redis_client"]
