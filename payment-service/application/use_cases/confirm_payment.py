import logging
import uuid

from application.dtos.payment_dtos import PaymentResponse
from domain.exceptions.payment_exceptions import (
    PaymentNotFoundException,
    UnauthorizedPaymentAccessException,
)
from domain.repositories.payment_repository import PaymentRepository
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.payment_events import PaymentConfirmed

logger = logging.getLogger(__name__)


class ConfirmPayment:
    """
    Marks a payment as CONFIRMED and publishes PaymentConfirmed.

    In the stub phase this generates a synthetic provider reference.
    When a real provider is integrated, the provider_reference will come
    from the webhook / synchronous confirmation response.

    Authorization: the caller must supply the user_id that owns the payment.
    """

    def __init__(
        self,
        payment_repo: PaymentRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._payment_repo = payment_repo
        self._event_publisher = event_publisher

    async def execute(self, payment_id: str, requesting_user_id: str) -> PaymentResponse:
        payment = await self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundException(payment_id)

        if payment.user_id != requesting_user_id:
            raise UnauthorizedPaymentAccessException()

        provider_reference = f"mock_ref_{uuid.uuid4().hex[:16]}"
        payment.confirm(provider_reference)
        payment = await self._payment_repo.update(payment)

        event = PaymentConfirmed(
            payment_id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=float(payment.amount_value),
            currency=payment.currency,
        )
        await self._event_publisher.publish("payment.events", event)

        return PaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=payment.amount_value,
            currency=payment.currency,
            status=payment.status.value,
            idempotency_key=payment.idempotency_key,
            provider_reference=payment.provider_reference,
            failure_reason=payment.failure_reason,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )


__all__ = ["ConfirmPayment"]
