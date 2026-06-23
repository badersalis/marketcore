import logging
from typing import List

from domain.repositories.product_repository import ProductRepository
from shared.events.product_events import ProductPublished

logger = logging.getLogger(__name__)


class PublishProduct:
    """Transitions a product from PROCESSING → LIVE and fires ProductPublished.

    Called by the completion aggregator when product.images_ready arrives.
    If a moderation step is added later, insert it between PROCESSING and LIVE
    by changing this use case to transition to UNDER_REVIEW instead, and add
    a separate ApproveProduct use case that does UNDER_REVIEW → LIVE.
    """

    def __init__(self, product_repo: ProductRepository, publisher=None, cache=None) -> None:
        self._product_repo = product_repo
        self._publisher = publisher
        self._cache = cache

    async def execute(self, product_id: str, cdn_urls: List[str], merchant_id: str = "") -> None:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            logger.error("PublishProduct: product %s not found", product_id)
            return

        try:
            product.mark_images_ready(cdn_urls)
        except Exception as exc:
            logger.warning("PublishProduct: %s — skipping (already %s?)", exc, product.status)
            return

        await self._product_repo.update(product)

        if self._cache:
            await self._cache.invalidate(product_id)
            await self._cache.invalidate_list()

        if self._publisher:
            await self._publisher.publish(
                "product.events",
                ProductPublished(
                    product_id=product.id,
                    merchant_id=merchant_id,
                    name=product.name,
                    image_urls=product.image_urls,
                ),
            )

        logger.info("Product %s is now LIVE (%d images)", product_id, len(cdn_urls))


__all__ = ["PublishProduct"]
