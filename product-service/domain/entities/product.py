from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.base_entity import BaseEntity
from shared.base_exception import DomainException
from domain.value_objects.money import Money


@dataclass
class Product(BaseEntity):
    name: str = ""
    description: str = ""
    price: Optional[Money] = None
    stock: int = 0
    category_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def adjust_stock(self, delta: int) -> None:
        new_stock = self.stock + delta
        if new_stock < 0:
            raise DomainException("Insufficient stock", "INSUFFICIENT_STOCK")
        self.stock = new_stock


__all__ = ["Product"]
