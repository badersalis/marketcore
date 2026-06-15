import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Numeric, String, Text

from infrastructure.persistence.database import Base


class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    idempotency_key = Column(String(255), unique=True, nullable=False, index=True)
    provider_reference = Column(String(255), nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)


__all__ = ["PaymentModel"]
