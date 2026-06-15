import json
import logging
import uuid
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from arq import ArqRedis
from asgi_correlation_id import correlation_id as _correlation_id_ctx

from core.config import ARQ_QUEUE_NAME

logger = logging.getLogger(__name__)

_HANDLED_EVENTS = {
    "user.registered",
    "user.verified",
    "user.verification_email_requested",
    "payment.confirmed",
    "payment.failed",
}


class NotificationConsumer:
    def __init__(self, rabbitmq_url: str, arq_pool: ArqRedis) -> None:
        self._url = rabbitmq_url
        self._arq = arq_pool
        self._connection: Optional[aio_pika.abc.AbstractRobustConnection] = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=10)

        await self._bind_exchange(channel, "user.events", "notification.user.events")
        await self._bind_exchange(channel, "payment.events", "notification.payment.events")

        logger.info("NotificationConsumer started — listening for events")

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def _bind_exchange(
        self, channel: aio_pika.abc.AbstractChannel, exchange_name: str, queue_name: str
    ) -> None:
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.FANOUT, durable=True
        )
        queue = await channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": f"{exchange_name}.dlx",
                "x-message-ttl": 86_400_000,  # 24 h
            },
        )
        await queue.bind(exchange)
        await queue.consume(self._handle_message)

    async def _handle_message(self, message: AbstractIncomingMessage) -> None:
        corr_id = message.correlation_id or str(uuid.uuid4())
        token = _correlation_id_ctx.set(corr_id)
        try:
            async with message.process(requeue=False):
                try:
                    body = json.loads(message.body)
                except json.JSONDecodeError:
                    logger.error("Received non-JSON message — discarding")
                    return

                event_type = body.get("event_type", "")
                if event_type not in _HANDLED_EVENTS:
                    return

                logger.info("Enqueueing job for event: %s", event_type)
                try:
                    await self._dispatch(event_type, body, corr_id)
                except Exception as exc:
                    logger.error("Failed to enqueue job for %s: %s", event_type, exc, exc_info=True)
        finally:
            _correlation_id_ctx.reset(token)

    async def _dispatch(self, event_type: str, body: dict, corr_id: str) -> None:
        kw = {"_queue_name": ARQ_QUEUE_NAME, "correlation_id": corr_id}

        if event_type in ("user.registered", "user.verification_email_requested"):
            email = body.get("email", "")
            otp = body.get("otp", "")
            if not email or not otp:
                logger.warning("Missing email/otp in %s — skipping", event_type)
                return
            await self._arq.enqueue_job("send_verification_email_job", to=email, otp=otp, **kw)

        elif event_type == "user.verified":
            email = body.get("email", "")
            if not email:
                logger.warning("Missing email in user.verified — skipping")
                return
            await self._arq.enqueue_job("send_welcome_email_job", to=email, **kw)

        elif event_type == "payment.confirmed":
            logger.info(
                "PaymentConfirmed for payment=%s order=%s — user email lookup not yet wired",
                body.get("payment_id"), body.get("order_id"),
            )

        elif event_type == "payment.failed":
            logger.info(
                "PaymentFailed for payment=%s order=%s — user email lookup not yet wired",
                body.get("payment_id"), body.get("order_id"),
            )


__all__ = ["NotificationConsumer"]
