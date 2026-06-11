from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def save(self, token: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def revoke(self, token: str) -> None:
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: str) -> None:
        pass


__all__ = ["RefreshTokenRepository"]
