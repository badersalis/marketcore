from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from shared.base_entity import BaseEntity
from domain.value_objects.money import Money
from domain.value_objects.order_status import OrderStatus
from domain.value_objects.shipping_address import ShippingAddress
from domain.exceptions.order_exceptions import (
    OrderAlreadyCancelledException,
    InvalidOrderStatusTransitionException,
)


@dataclass
class OrderItem:
    product_id: str
    sku_id: Optional[str]
    name: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Order(BaseEntity):
    user_id: str = ""
    status: OrderStatus = OrderStatus.PENDING
    items: List[OrderItem] = field(default_factory=list)
    total: Optional[Money] = None
    shipping_address: Optional[ShippingAddress] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    _VALID_TRANSITIONS = {
        OrderStatus.PENDING: {OrderStatus.PAYING, OrderStatus.CANCELLED},
        OrderStatus.PAYING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.FULFILLING, OrderStatus.CANCELLED},
        OrderStatus.FULFILLING: {OrderStatus.SHIPPED},
        OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
        OrderStatus.DELIVERED: set(),
        OrderStatus.CANCELLED: set(),
    }

    def transition_to(self, new_status: OrderStatus) -> None:
        allowed = self._VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidOrderStatusTransitionException(self.status, new_status)
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def cancel(self, reason: str = "") -> None:
        if not self.status.is_cancellable:
            raise OrderAlreadyCancelledException(self.id)
        self.transition_to(OrderStatus.CANCELLED)

    @property
    def computed_total(self) -> Money:
        if not self.items:
            return Money(amount=Decimal("0"), currency="USD")
        result = self.items[0].subtotal
        for item in self.items[1:]:
            result = result + item.subtotal
        return result


__all__ = ["Order", "OrderItem"]
