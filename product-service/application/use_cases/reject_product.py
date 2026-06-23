import logging

from domain.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)


class RejectProduct:
    """Transitions a product to REJECTED after permanent image-processing failure."""

    def __init__(self, product_repo: ProductRepository) -> None:
        self._product_repo = product_repo

    async def execute(self, product_id: str, reason: str = "") -> None:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            logger.error("RejectProduct: product %s not found", product_id)
            return
        product.reject(reason)
        await self._product_repo.update(product)
        logger.warning("Product %s REJECTED: %s", product_id, reason)


__all__ = ["RejectProduct"]
