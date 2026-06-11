from dataclasses import dataclass, field
from typing import Dict, Any
from shared.base_event import DomainEvent


@dataclass
class OrderPlaced(DomainEvent):
    order_id: str = ""
    user_id: str = ""
    total_amount: float = 0.0
    currency: str = "USD"
    event_type: str = field(default="order.placed")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "order_id": self.order_id,
            "user_id": self.user_id,
            "total_amount": self.total_amount,
            "currency": self.currency,
        })
        return d


@dataclass
class OrderCancelled(DomainEvent):
    order_id: str = ""
    user_id: str = ""
    reason: str = ""
    event_type: str = field(default="order.cancelled")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "order_id": self.order_id,
            "user_id": self.user_id,
            "reason": self.reason,
        })
        return d


__all__ = ["OrderPlaced", "OrderCancelled"]
