from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class UserProfile:
    user_id: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update(
        self,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> None:
        if display_name is not None:
            self.display_name = display_name
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if bio is not None:
            self.bio = bio
        if phone is not None:
            self.phone = phone
        self.updated_at = datetime.now(timezone.utc)


__all__ = ["UserProfile"]
