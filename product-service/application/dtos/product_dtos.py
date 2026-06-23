from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

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
    image_urls: List[str] = []

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


class SkuResponse(BaseModel):
    id: str
    product_id: str
    code: str
    attributes: Dict[str, str] = {}
    price: Optional[Decimal] = None   # None → inherits product price
    currency: Optional[str] = None
    stock: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateSkuRequest(BaseModel):
    code: str
    attributes: Dict[str, str] = {}
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    stock: int = 0

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("price must be non-negative")
        return v

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("code must not be blank")
        return v.strip().upper()


class UpdateSkuRequest(BaseModel):
    code: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: Decimal
    currency: str
    stock: int
    category_id: Optional[str]
    is_active: bool
    status: str
    image_urls: List[str] = []
    created_at: datetime
    skus: List[SkuResponse] = []

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
    "SkuResponse",
    "CreateSkuRequest",
    "UpdateSkuRequest",
    "ProductResponse",
    "ProductListResponse",
]
