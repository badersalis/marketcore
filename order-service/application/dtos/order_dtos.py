from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from domain.value_objects.order_status import OrderStatus


class ShippingAddressDTO(BaseModel):
    full_name: str
    line1: str
    line2: Optional[str] = None
    city: str
    country: str
    postal_code: str


class AddToCartRequest(BaseModel):
    product_id: str
    sku_id: Optional[str] = None
    quantity: int = Field(..., ge=1, le=100)


class RemoveFromCartRequest(BaseModel):
    sku_id: Optional[str] = None


class PlaceOrderRequest(BaseModel):
    shipping_address: ShippingAddressDTO


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class CartItemResponse(BaseModel):
    product_id: str
    sku_id: Optional[str]
    name: str
    unit_price: str
    currency: str
    quantity: int
    subtotal: str

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItemResponse]
    total: str
    currency: str

    model_config = {"from_attributes": True}


class OrderItemResponse(BaseModel):
    product_id: str
    sku_id: Optional[str]
    name: str
    unit_price: str
    currency: str
    quantity: int
    subtotal: str

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: str
    user_id: str
    status: OrderStatus
    items: List[OrderItemResponse]
    total: str
    currency: str
    shipping_address: Optional[ShippingAddressDTO]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = [
    "ShippingAddressDTO",
    "AddToCartRequest",
    "RemoveFromCartRequest",
    "PlaceOrderRequest",
    "UpdateOrderStatusRequest",
    "CartItemResponse",
    "CartResponse",
    "OrderItemResponse",
    "OrderResponse",
]
