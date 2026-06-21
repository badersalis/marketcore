import logging
from typing import Optional

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

_KEY_PREFIX = "product:"
_TTL = 3600  # seconds


class ProductCache:
    def __init__(self, redis_url: str) -> None:
        self._client: Optional[aioredis.Redis] = None
        self._url = redis_url

    async def connect(self) -> None:
        self._client = aioredis.from_url(self._url, decode_responses=True)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def invalidate(self, product_id: str) -> None:
        if not self._client:
            return
        key = f"{_KEY_PREFIX}{product_id}"
        await self._client.delete(key)
        logger.debug("Cache invalidated: %s", key)

    async def invalidate_list(self) -> None:
        """Bust the product-list cache so newly LIVE products appear in listings."""
        if not self._client:
            return
        async for key in self._client.scan_iter(f"{_KEY_PREFIX}list:*"):
            await self._client.delete(key)
            logger.debug("Cache invalidated: %s", key)


__all__ = ["ProductCache"]
