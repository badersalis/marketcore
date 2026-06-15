import json
import logging
from typing import Optional

import aio_pika

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

    async def publish(self, exchange_name: str, event: DomainEvent) -> None:
        if not self._channel:
            logger.warning("RabbitMQ not connected — skipping publish of %s", event.event_type)
            return
        try:
            exchange = await self._channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.FANOUT, durable=True
            )
            body = json.dumps(event.to_dict()).encode()
            message = aio_pika.Message(
                body=body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key="")
            logger.debug("Published %s to exchange '%s'", event.event_type, exchange_name)
        except Exception as exc:
            logger.error("Failed to publish event %s: %s", event.event_type, exc)


__all__ = ["EventPublisher"]
