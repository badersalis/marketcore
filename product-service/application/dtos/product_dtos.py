from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator


class CreateCategoryRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CreateProductRequest(BaseModel):
    name: str
    description: str = ""
    price: Decimal
    currency: str = "USD"
    stock: int = 0
    category_id: Optional[str] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("price must be non-negative")
        return v


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    stock: Optional[int] = None
    category_id: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: Decimal
    currency: str
    stock: int
    category_id: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    skip: int
    limit: int


__all__ = [
    "CreateCategoryRequest",
    "CategoryResponse",
    "CreateProductRequest",
    "UpdateProductRequest",
    "ProductResponse",
    "ProductListResponse",
]
