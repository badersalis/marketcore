from dataclasses import dataclass, field
from typing import Dict, Any
from shared.base_event import DomainEvent


@dataclass
class UserRegistered(DomainEvent):
    user_id: str = ""
    email: str = ""
    otp: str = ""
    event_type: str = field(default="user.registered")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "email": self.email,
            "otp": self.otp,
        })
        return d


@dataclass
class VerificationEmailRequested(DomainEvent):
    """Published when a user requests a new OTP verification email (resend)."""
    user_id: str = ""
    email: str = ""
    otp: str = ""
    event_type: str = field(default="user.verification_email_requested")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "email": self.email,
            "otp": self.otp,
        })
        return d


@dataclass
class UserVerified(DomainEvent):
    """Published when a user successfully verifies their email address."""
    user_id: str = ""
    email: str = ""
    event_type: str = field(default="user.verified")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "email": self.email,
        })
        return d


@dataclass
class MerchantUpgradeRequested(DomainEvent):
    user_id: str = ""
    email: str = ""
    request_id: str = ""
    event_type: str = field(default="user.merchant_upgrade_requested")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "email": self.email,
            "request_id": self.request_id,
        })
        return d


@dataclass
class MerchantApproved(DomainEvent):
    user_id: str = ""
    email: str = ""
    event_type: str = field(default="user.merchant_approved")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "email": self.email,
        })
        return d


@dataclass
class KYCInquiryCreated(DomainEvent):
    """Published when a user initiates a KYC inquiry via Persona."""
    user_id: str = ""
    inquiry_id: str = ""
    persona_inquiry_id: str = ""
    event_type: str = field(default="user.kyc_inquiry_created")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "inquiry_id": self.inquiry_id,
            "persona_inquiry_id": self.persona_inquiry_id,
        })
        return d


@dataclass
class KYCStatusUpdated(DomainEvent):
    """Published after Persona webhook is processed and inquiry status changes."""
    user_id: str = ""
    inquiry_id: str = ""
    new_status: str = ""
    event_type: str = field(default="user.kyc_status_updated")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "inquiry_id": self.inquiry_id,
            "new_status": self.new_status,
        })
        return d


__all__ = [
    "UserRegistered",
    "UserVerified",
    "VerificationEmailRequested",
    "MerchantUpgradeRequested",
    "MerchantApproved",
    "KYCInquiryCreated",
    "KYCStatusUpdated",
]
