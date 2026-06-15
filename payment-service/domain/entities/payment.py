from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from shared.base_entity import BaseEntity
from domain.value_objects.money import Money
from domain.value_objects.payment_status import PaymentStatus
from domain.exceptions.payment_exceptions import InvalidPaymentTransitionException


@dataclass
class Payment(BaseEntity):
    """
    Payment aggregate root.

    State transitions:
        PENDING  → PROCESSING  (when submitted to a provider — future)
        PENDING  → CANCELLED   (cancel before processing)
        PROCESSING → CONFIRMED (provider confirms)
        PROCESSING → FAILED    (provider declines / timeout)

    In the current stub, confirm() moves directly from PENDING to CONFIRMED
    to allow end-to-end testing without a real provider.
    """

    order_id: str = ""
    user_id: str = ""
    amount: Optional[Money] = None
    status: PaymentStatus = PaymentStatus.PENDING
    idempotency_key: str = ""
    provider_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # ── factory ────────────────────────────────────────────────────────────────

    @classmethod
    def initiate(
        cls,
        order_id: str,
        user_id: str,
        amount: Money,
        idempotency_key: str,
    ) -> "Payment":
        return cls(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
        )

    # ── state transitions ──────────────────────────────────────────────────────

    def mark_processing(self) -> None:
        self._require_status(PaymentStatus.PENDING, target=PaymentStatus.PROCESSING)
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def confirm(self, provider_reference: str) -> None:
        allowed = {PaymentStatus.PENDING, PaymentStatus.PROCESSING}
        if self.status not in allowed:
            raise InvalidPaymentTransitionException(self.status, PaymentStatus.CONFIRMED)
        self.status = PaymentStatus.CONFIRMED
        self.provider_reference = provider_reference
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def fail(self, reason: str) -> None:
        allowed = {PaymentStatus.PENDING, PaymentStatus.PROCESSING}
        if self.status not in allowed:
            raise InvalidPaymentTransitionException(self.status, PaymentStatus.FAILED)
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def cancel(self) -> None:
        self._require_status(PaymentStatus.PENDING, target=PaymentStatus.CANCELLED)
        self.status = PaymentStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    # ── helpers ────────────────────────────────────────────────────────────────

    def _require_status(self, current: PaymentStatus, target: PaymentStatus) -> None:
        if self.status != current:
            raise InvalidPaymentTransitionException(self.status, target)

    @property
    def amount_value(self) -> Decimal:
        return self.amount.amount if self.amount else Decimal("0")

    @property
    def currency(self) -> str:
        return self.amount.currency if self.amount else "USD"


__all__ = ["Payment"]
