import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from domain.value_objects.role import UserRole
from infrastructure.persistence.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.MEMBER,
    )
    is_merchant_approved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", lazy="select")
    merchant_requests = relationship("MerchantUpgradeRequestModel", back_populates="user", lazy="select")


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(Text, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("UserModel", back_populates="refresh_tokens")


class MerchantUpgradeRequestModel(Base):
    __tablename__ = "merchant_upgrade_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(String, nullable=True)

    user = relationship("UserModel", back_populates="merchant_requests")


__all__ = ["UserModel", "RefreshTokenModel", "MerchantUpgradeRequestModel"]
