from dataclasses import dataclass, field
from typing import Dict, Any
from shared.base_event import DomainEvent


@dataclass
class PaymentConfirmed(DomainEvent):
    payment_id: str = ""
    order_id: str = ""
    user_id: str = ""
    amount: float = 0.0
    currency: str = "USD"
    event_type: str = field(default="payment.confirmed")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
        })
        return d


@dataclass
class PaymentFailed(DomainEvent):
    payment_id: str = ""
    order_id: str = ""
    user_id: str = ""
    reason: str = ""
    event_type: str = field(default="payment.failed")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "reason": self.reason,
        })
        return d


__all__ = ["PaymentConfirmed", "PaymentFailed"]
