from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.cart import Cart


class CartRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Cart]: ...

    @abstractmethod
    async def save(self, cart: Cart) -> Cart: ...

    @abstractmethod
    async def delete(self, user_id: str) -> None: ...


__all__ = ["CartRepository"]
