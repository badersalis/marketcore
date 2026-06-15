import logging
from decimal import Decimal

from application.dtos.payment_dtos import CreatePaymentIntentRequest, PaymentResponse
from domain.entities.payment import Payment
from domain.exceptions.payment_exceptions import DuplicateIdempotencyKeyException
from domain.repositories.payment_repository import PaymentRepository
from domain.value_objects.money import Money
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.payment_events import PaymentCreated

logger = logging.getLogger(__name__)


class CreatePaymentIntent:
    """
    Initiates a new payment and persists it as PENDING.

    Idempotency contract:
        If a payment with the same idempotency_key already exists AND its
        (order_id, user_id, amount, currency) match → return the existing payment
        (safe retry).  If any field differs → raise DuplicateIdempotencyKeyException
        (caller error — different intent, same key).
    """

    def __init__(
        self,
        payment_repo: PaymentRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._payment_repo = payment_repo
        self._event_publisher = event_publisher

    async def execute(self, request: CreatePaymentIntentRequest) -> PaymentResponse:
        existing = await self._payment_repo.get_by_idempotency_key(request.idempotency_key)
        if existing:
            self._assert_idempotent_match(existing, request)
            logger.info("Idempotent replay for key=%s payment=%s", request.idempotency_key, existing.id)
            return self._to_response(existing)

        amount = Money(amount=Decimal(str(request.amount)), currency=request.currency)
        payment = Payment.initiate(
            order_id=request.order_id,
            user_id=request.user_id,
            amount=amount,
            idempotency_key=request.idempotency_key,
        )
        payment = await self._payment_repo.save(payment)

        event = PaymentCreated(
            payment_id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=float(payment.amount_value),
            currency=payment.currency,
            idempotency_key=payment.idempotency_key,
        )
        await self._event_publisher.publish("payment.events", event)

        return self._to_response(payment)

    def _assert_idempotent_match(
        self, existing: Payment, request: CreatePaymentIntentRequest
    ) -> None:
        if (
            existing.order_id != request.order_id
            or existing.user_id != request.user_id
            or existing.amount_value != Decimal(str(request.amount))
            or existing.currency != request.currency.upper()
        ):
            raise DuplicateIdempotencyKeyException(request.idempotency_key)

    def _to_response(self, payment: Payment) -> PaymentResponse:
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


__all__ = ["CreatePaymentIntent"]
