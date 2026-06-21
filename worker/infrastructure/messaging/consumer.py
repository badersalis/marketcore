import json
import logging
import uuid
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from arq import ArqRedis

logger = logging.getLogger(__name__)

_IMAGE_JOB_TIMEOUT = 120  # seconds — image processing can take longer than email jobs


class ProductEventConsumer:
    """Consumes product.events from RabbitMQ and dispatches image-processing ARQ jobs."""

    def __init__(self, rabbitmq_url: str, arq_pool: ArqRedis) -> None:
        self._url = rabbitmq_url
        self._arq = arq_pool
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=5)

        exchange = await channel.declare_exchange(
            "product.events", aio_pika.ExchangeType.FANOUT, durable=True
        )
        queue = await channel.declare_queue(
            "worker.product.events",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "product.events.dlx",
                "x-message-ttl": 86_400_000,
            },
        )
        await queue.bind(exchange)
        await queue.consume(self._handle)
        logger.info("ProductEventConsumer started")

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def _handle(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                body = json.loads(message.body)
            except json.JSONDecodeError:
                logger.error("Non-JSON message on product.events — discarding")
                return

            event_type = body.get("event_type", "")
            if event_type != "product.created":
                return  # other product events are not our concern here

            product_id = body.get("product_id", "")
            raw_image_urls = body.get("raw_image_urls", [])
            corr_id = message.correlation_id or str(uuid.uuid4())

            if not product_id:
                logger.warning("product.created missing product_id — skipping")
                return

            logger.info("Enqueueing image processing for product %s (%d images)", product_id, len(raw_image_urls))
            await self._arq.enqueue_job(
                "process_product_images_job",
                product_id=product_id,
                raw_image_urls=raw_image_urls,
                correlation_id=corr_id,
                _job_id=f"img:{product_id}",       # idempotent: one job per product
                _job_timeout=_IMAGE_JOB_TIMEOUT,
            )


__all__ = ["ProductEventConsumer"]
