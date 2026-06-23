from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.base_entity import BaseEntity
from domain.value_objects.email import Email
from domain.value_objects.hashed_password import HashedPassword
from domain.value_objects.role import UserRole


@dataclass
class User(BaseEntity):
    email: Optional[Email] = None
    hashed_password: Optional[HashedPassword] = None
    is_active: bool = True
    is_verified: bool = False
    role: UserRole = UserRole.MEMBER
    is_merchant_approved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        self.is_active = False

    def verify(self) -> None:
        self.is_verified = True

    def assign_role(self, role: UserRole) -> None:
        self.role = role

    def approve_merchant(self) -> None:
        self.role = UserRole.MERCHANT
        self.is_merchant_approved = True


__all__ = ["User"]
