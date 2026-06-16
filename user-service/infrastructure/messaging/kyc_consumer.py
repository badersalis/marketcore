import json
import logging
from typing import Callable, Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger(__name__)

_EXCHANGE = "kyc.webhooks"
_QUEUE = "user-service.kyc.webhooks"
_DLX_EXCHANGE = "kyc.webhooks.dlx"
_DLX_QUEUE = "user-service.kyc.webhooks.dead"


class KYCWebhookConsumer:
    def __init__(self, rabbitmq_url: str) -> None:
        self._url = rabbitmq_url
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None
        self._channel: Optional[aio_pika.abc.AbstractChannel] = None

    async def start(self, handler: Callable) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)

        dlx = await self._channel.declare_exchange(
            _DLX_EXCHANGE, aio_pika.ExchangeType.FANOUT, durable=True
        )
        dlq = await self._channel.declare_queue(_DLX_QUEUE, durable=True)
        await dlq.bind(dlx)

        exchange = await self._channel.declare_exchange(
            _EXCHANGE, aio_pika.ExchangeType.FANOUT, durable=True
        )
        queue = await self._channel.declare_queue(
            _QUEUE,
            durable=True,
            arguments={
                "x-dead-letter-exchange": _DLX_EXCHANGE,
                "x-message-ttl": 30_000,
            },
        )
        await queue.bind(exchange)

        async def _on_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body)
                    await handler(payload)
                except Exception as exc:
                    logger.error("KYC webhook processing failed: %s", exc, exc_info=True)
                    raise

        await queue.consume(_on_message)
        logger.info("KYC webhook consumer started on %s", _QUEUE)

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()


__all__ = ["KYCWebhookConsumer"]
