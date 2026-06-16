import logging
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.config import settings

logger = logging.getLogger(__name__)


class ProductServiceClient:
    """Async HTTP client for product-service with circuit-breaker retry logic."""

    def __init__(self) -> None:
        self._base_url = settings.PRODUCT_SERVICE_URL

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def get_product(self, product_id: str) -> Optional[dict]:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=5.0) as client:
            response = client.get(f"/products/{product_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def check_stock(self, product_id: str, sku_id: Optional[str], quantity: int) -> dict:
        """Returns {"available": bool, "stock": int, "price": str, "name": str}."""
        async with httpx.AsyncClient(base_url=self._base_url, timeout=5.0) as client:
            response = await client.get(f"/products/{product_id}")
            if response.status_code == 404:
                return {"available": False, "stock": 0, "price": "0", "name": ""}
            response.raise_for_status()
            data = response.json()

            if sku_id:
                for sku in data.get("skus", []):
                    if sku["id"] == sku_id:
                        return {
                            "available": sku.get("stock", 0) >= quantity and sku.get("is_active", True),
                            "stock": sku.get("stock", 0),
                            "price": sku.get("price") or data.get("price", "0"),
                            "name": data.get("name", ""),
                        }
                return {"available": False, "stock": 0, "price": "0", "name": ""}

            return {
                "available": data.get("stock", 0) >= quantity and data.get("is_active", True),
                "stock": data.get("stock", 0),
                "price": data.get("price", "0"),
                "name": data.get("name", ""),
            }


__all__ = ["ProductServiceClient"]
