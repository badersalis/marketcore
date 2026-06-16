from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYING = "paying"
    CONFIRMED = "confirmed"
    FULFILLING = "fulfilling"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)

    @property
    def is_cancellable(self) -> bool:
        return self in (OrderStatus.PENDING, OrderStatus.PAYING, OrderStatus.CONFIRMED)


__all__ = ["OrderStatus"]
