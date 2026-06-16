import json
import logging
from typing import Optional

import aio_pika
from asgi_correlation_id import correlation_id as _correlation_id_ctx

from shared.base_event import DomainEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, rabbitmq_url: str) -> None:
        self._url = rabbitmq_url
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None
        self._channel: Optional[aio_pika.abc.AbstractChannel] = None

    async def connect(self) -> None:
        try:
            self._connection = await aio_pika.connect_robust(self._url)
            self._channel = await self._connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as exc:
            logger.error("Failed to connect to RabbitMQ: %s", exc)

    async def disconnect(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def publish(self, event: DomainEvent, *, exchange: str = "user.events") -> None:
        await self._publish_bytes(
            exchange,
            json.dumps(event.to_dict()).encode(),
        )

    async def publish_raw(self, exchange: str, body: bytes) -> None:
        """Publish raw bytes — used to forward Persona webhook payloads to the KYC queue."""
        await self._publish_bytes(exchange, body)

    async def _publish_bytes(self, exchange_name: str, body: bytes) -> None:
        if not self._channel:
            logger.warning("RabbitMQ not connected — skipping publish to %s", exchange_name)
            return
        try:
            exchange = await self._channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.FANOUT, durable=True
            )
            corr_id = _correlation_id_ctx.get(None)
            message = aio_pika.Message(
                body=body,
                content_type="application/json",
                correlation_id=corr_id,
            )
            await exchange.publish(message, routing_key="")
            logger.debug("Published to %s (correlation_id=%s)", exchange_name, corr_id)
        except Exception as exc:
            logger.error("Failed to publish to %s: %s", exchange_name, exc)


__all__ = ["EventPublisher"]
