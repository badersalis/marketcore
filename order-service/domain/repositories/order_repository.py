from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.order import Order
from domain.value_objects.order_status import OrderStatus


class OrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Order]: ...

    @abstractmethod
    async def save(self, order: Order) -> Order: ...

    @abstractmethod
    async def update(self, order: Order) -> Order: ...


__all__ = ["OrderRepository"]
