from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from shared.base_entity import BaseEntity
from shared.base_exception import DomainException
from domain.value_objects.money import Money


class ProductStatus(str, Enum):
    PROCESSING = "processing"  # images being processed after creation
    # UNDER_REVIEW = "under_review"  # future moderation gate — insert between PROCESSING and LIVE
    LIVE = "live"              # published and visible to buyers
    REJECTED = "rejected"      # image processing failed permanently


@dataclass
class Product(BaseEntity):
    name: str = ""
    description: str = ""
    price: Optional[Money] = None
    stock: int = 0
    category_id: Optional[str] = None
    is_active: bool = True
    status: ProductStatus = ProductStatus.PROCESSING
    image_urls: List[str] = field(default_factory=list)
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

    def mark_images_ready(self, cdn_urls: List[str]) -> None:
        if self.status != ProductStatus.PROCESSING:
            raise DomainException(
                f"Cannot mark images ready from status '{self.status}'",
                "INVALID_STATUS_TRANSITION",
            )
        self.image_urls = cdn_urls
        self.status = ProductStatus.LIVE

    def reject(self, reason: str = "") -> None:
        self.status = ProductStatus.REJECTED


__all__ = ["Product", "ProductStatus"]
