from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from shared.base_entity import BaseEntity
from domain.value_objects.money import Money


@dataclass
class CartItem:
    product_id: str
    sku_id: Optional[str]
    name: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Cart(BaseEntity):
    user_id: str = ""
    items: List[CartItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_item(self, item: CartItem) -> None:
        for existing in self.items:
            if existing.product_id == item.product_id and existing.sku_id == item.sku_id:
                existing.quantity += item.quantity
                self.updated_at = datetime.utcnow()
                return
        self.items.append(item)
        self.updated_at = datetime.utcnow()

    def remove_item(self, product_id: str, sku_id: Optional[str] = None) -> None:
        self.items = [
            i for i in self.items
            if not (i.product_id == product_id and i.sku_id == sku_id)
        ]
        self.updated_at = datetime.utcnow()

    @property
    def total(self) -> Money:
        if not self.items:
            return Money(amount=Decimal("0"), currency="USD")
        result = self.items[0].subtotal
        for item in self.items[1:]:
            result = result + item.subtotal
        return result

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0


__all__ = ["Cart", "CartItem"]
