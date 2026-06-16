import json
import logging
import uuid
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from asgi_correlation_id import correlation_id as _correlation_id_ctx

logger = logging.getLogger(__name__)

_HANDLED_EVENTS = {"payment.confirmed", "payment.failed"}


class PaymentEventConsumer:
    """Consumes payment.events FANOUT exchange to update order state."""

    def __init__(self, rabbitmq_url: str, order_handler) -> None:
        self._url = rabbitmq_url
        self._handler = order_handler
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            "payment.events", aio_pika.ExchangeType.FANOUT, durable=True
        )
        queue = await channel.declare_queue(
            "order-service.payment.events",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "payment.events.dlx",
                "x-message-ttl": 86_400_000,
            },
        )
        await queue.bind(exchange)
        await queue.consume(self._handle_message)
        logger.info("PaymentEventConsumer started")

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def _handle_message(self, message: AbstractIncomingMessage) -> None:
        corr_id = message.correlation_id or str(uuid.uuid4())
        token = _correlation_id_ctx.set(corr_id)
        try:
            async with message.process(requeue=False):
                try:
                    body = json.loads(message.body)
                except json.JSONDecodeError:
                    logger.error("Non-JSON payment event — discarding")
                    return

                event_type = body.get("event_type", "")
                if event_type not in _HANDLED_EVENTS:
                    return

                logger.info("Handling payment event: %s", event_type)
                await self._handler(event_type, body)
        except Exception as exc:
            logger.error("Error handling payment event: %s", exc, exc_info=True)
        finally:
            _correlation_id_ctx.reset(token)


__all__ = ["PaymentEventConsumer"]
