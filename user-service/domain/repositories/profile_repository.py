from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.user_profile import UserProfile


class ProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]: ...

    @abstractmethod
    async def save(self, profile: UserProfile) -> UserProfile: ...


__all__ = ["ProfileRepository"]
