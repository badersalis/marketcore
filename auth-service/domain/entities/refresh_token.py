from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.base_entity import BaseEntity


@dataclass
class RefreshToken(BaseEntity):
    user_id: str = ""
    token: str = ""
    expires_at: Optional[datetime] = None
    is_revoked: bool = False

    def revoke(self) -> None:
        self.is_revoked = True

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return True
        return datetime.utcnow() > self.expires_at


__all__ = ["RefreshToken"]
