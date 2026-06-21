import json
import logging
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger(__name__)

_HANDLED = {"product.images_ready", "product.images_failed"}


class ProductEventConsumer:
    """Consumes completion events from product.events and drives status transitions.

    Listens for:
      - product.images_ready  → transition PROCESSING → LIVE, emit product.published
      - product.images_failed → transition to REJECTED
    """

    def __init__(self, rabbitmq_url: str, handler) -> None:
        self._url = rabbitmq_url
        self._handler = handler  # async callable(event_type, body) → None
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            "product.events", aio_pika.ExchangeType.FANOUT, durable=True
        )
        queue = await channel.declare_queue(
            "product-service.product.events",
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
                logger.error("Non-JSON message — discarding")
                return

            event_type = body.get("event_type", "")
            if event_type not in _HANDLED:
                return

            try:
                await self._handler(event_type, body)
            except Exception as exc:
                logger.error("Error handling %s: %s", event_type, exc, exc_info=True)


__all__ = ["ProductEventConsumer"]
