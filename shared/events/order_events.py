from dataclasses import dataclass, field
from typing import Dict, Any, List
from shared.base_event import DomainEvent


@dataclass
class OrderPlaced(DomainEvent):
    order_id: str = ""
    user_id: str = ""
    items: List[dict] = field(default_factory=list)
    total_amount: str = "0.00"
    currency: str = "USD"
    event_type: str = field(default="order.placed")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "order_id": self.order_id,
            "user_id": self.user_id,
            "items": self.items,
            "total_amount": self.total_amount,
            "currency": self.currency,
        })
        return d


@dataclass
class OrderCancelled(DomainEvent):
    order_id: str = ""
    user_id: str = ""
    reason: str = ""
    refund_amount: str = "0.00"
    event_type: str = field(default="order.cancelled")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "order_id": self.order_id,
            "user_id": self.user_id,
            "reason": self.reason,
            "refund_amount": self.refund_amount,
        })
        return d


@dataclass
class OrderPaymentConfirmed(DomainEvent):
    order_id: str = ""
    payment_reference: str = ""
    event_type: str = field(default="order.payment_confirmed")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "order_id": self.order_id,
            "payment_reference": self.payment_reference,
        })
        return d


@dataclass
class OrderShipped(DomainEvent):
    order_id: str = ""
    tracking_code: str = ""
    carrier: str = ""
    event_type: str = field(default="order.shipped")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "order_id": self.order_id,
            "tracking_code": self.tracking_code,
            "carrier": self.carrier,
        })
        return d


@dataclass
class OrderDelivered(DomainEvent):
    order_id: str = ""
    event_type: str = field(default="order.delivered")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({"order_id": self.order_id})
        return d


__all__ = [
    "OrderPlaced",
    "OrderCancelled",
    "OrderPaymentConfirmed",
    "OrderShipped",
    "OrderDelivered",
]
