from dataclasses import dataclass, field
from typing import Any, Dict, List

from shared.base_event import DomainEvent


@dataclass
class ProductCreated(DomainEvent):
    product_id: str = ""
    merchant_id: str = ""
    name: str = ""
    raw_image_urls: List[str] = field(default_factory=list)
    event_type: str = field(default="product.created")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "product_id": self.product_id,
            "merchant_id": self.merchant_id,
            "name": self.name,
            "raw_image_urls": self.raw_image_urls,
        })
        return d


@dataclass
class ProductImagesReady(DomainEvent):
    product_id: str = ""
    cdn_urls: List[str] = field(default_factory=list)
    event_type: str = field(default="product.images_ready")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "product_id": self.product_id,
            "cdn_urls": self.cdn_urls,
        })
        return d


@dataclass
class ProductImagesFailed(DomainEvent):
    product_id: str = ""
    reason: str = ""
    event_type: str = field(default="product.images_failed")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "product_id": self.product_id,
            "reason": self.reason,
        })
        return d


@dataclass
class ProductPublished(DomainEvent):
    product_id: str = ""
    merchant_id: str = ""
    name: str = ""
    image_urls: List[str] = field(default_factory=list)
    event_type: str = field(default="product.published")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "product_id": self.product_id,
            "merchant_id": self.merchant_id,
            "name": self.name,
            "image_urls": self.image_urls,
        })
        return d


__all__ = [
    "ProductCreated",
    "ProductImagesReady",
    "ProductImagesFailed",
    "ProductPublished",
]
