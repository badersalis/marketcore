from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ShippingAddress:
    full_name: str
    line1: str
    city: str
    country: str
    postal_code: str
    line2: Optional[str] = None


__all__ = ["ShippingAddress"]
