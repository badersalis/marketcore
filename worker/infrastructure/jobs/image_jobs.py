import logging
import uuid
from typing import List

import httpx

from shared.events.product_events import ProductImagesFailed, ProductImagesReady

logger = logging.getLogger(__name__)

_DOWNLOAD_TIMEOUT = 30.0


async def process_product_images_job(
    ctx: dict,
    *,
    product_id: str,
    raw_image_urls: List[str],
    correlation_id: str = "",
) -> None:
    """Download raw images, process them, upload to storage, and emit the result event.

    ARQ retries this job up to ARQ_MAX_TRIES times with exponential backoff on any
    unhandled exception. On permanent failure (all retries exhausted) ARQ marks the
    job as failed — the caller can check the result key in Redis if needed.
    """
    from asgi_correlation_id import correlation_id as _corr_id_ctx
    token = _corr_id_ctx.set(correlation_id) if correlation_id else None

    publisher = ctx["event_publisher"]
    processor = ctx["image_processor"]
    storage = ctx["storage_client"]

    try:
        if not raw_image_urls:
            # No images to process — flip immediately to allow products without images.
            await publisher.publish(
                "product.events",
                ProductImagesReady(product_id=product_id, cdn_urls=[]),
            )
            logger.info("product %s has no images — emitted images_ready immediately", product_id)
            return

        cdn_urls: List[str] = []
        async with httpx.AsyncClient(timeout=_DOWNLOAD_TIMEOUT) as client:
            for idx, url in enumerate(raw_image_urls):
                raw = await _download(client, url, product_id, idx)

                result = processor.process(raw)

                slug = str(uuid.uuid4())
                full_url = await storage.upload(result.full, f"{product_id}/{slug}.webp")
                thumb_url = await storage.upload(result.thumb, f"{product_id}/{slug}_thumb.webp")

                cdn_urls.extend([full_url, thumb_url])
                logger.info(
                    "product %s image %d/%d processed (%s → %s)",
                    product_id, idx + 1, len(raw_image_urls),
                    result.original_size, result.final_size,
                )

        await publisher.publish(
            "product.events",
            ProductImagesReady(product_id=product_id, cdn_urls=cdn_urls),
        )
        logger.info("product %s images_ready — %d CDN URLs", product_id, len(cdn_urls))

    except Exception as exc:
        logger.error("Image processing failed for product %s: %s", product_id, exc, exc_info=True)
        # Re-raise so ARQ retries. After max_tries the job is marked failed and
        # ARQ will not retry further — at that point we emit images_failed.
        job = ctx.get("job")
        if job and job.attempt >= ctx.get("_max_tries", 5):
            await publisher.publish(
                "product.events",
                ProductImagesFailed(product_id=product_id, reason=str(exc)),
            )
        raise
    finally:
        if token is not None:
            _corr_id_ctx.reset(token)


async def _download(client: httpx.AsyncClient, url: str, product_id: str, idx: int) -> bytes:
    logger.debug("Downloading image %d for product %s: %s", idx, product_id, url)
    response = await client.get(url, follow_redirects=True)
    response.raise_for_status()
    return response.content


__all__ = ["process_product_images_job"]
