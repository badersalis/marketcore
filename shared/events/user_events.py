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


__all__ = ["UserRegistered", "UserVerified", "VerificationEmailRequested"]
