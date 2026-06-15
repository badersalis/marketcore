from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CreatePaymentIntentRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=255)
    user_id: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=Decimal("0"), decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    idempotency_key: str = Field(..., min_length=1, max_length=255)

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        return v.upper()

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_to_decimal(cls, v: object) -> Decimal:
        return Decimal(str(v))


class ConfirmPaymentRequest(BaseModel):
    """
    Intentionally empty for the stub phase.
    When a real provider is integrated, add provider_payload: dict here.
    """
    pass


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: Decimal
    currency: str
    status: str
    idempotency_key: str
    provider_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    offset: int
    limit: int


__all__ = [
    "CreatePaymentIntentRequest",
    "ConfirmPaymentRequest",
    "PaymentResponse",
    "PaymentListResponse",
]
