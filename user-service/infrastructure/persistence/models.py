from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from domain.value_objects.kyc_status import KYCStatus
from infrastructure.persistence.database import Base


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class KYCInquiryModel(Base):
    __tablename__ = "kyc_inquiries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    persona_inquiry_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    redirect_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[KYCStatus] = mapped_column(
        Enum(KYCStatus, name="kyc_status"), nullable=False, default=KYCStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


__all__ = ["UserProfileModel", "KYCInquiryModel"]
