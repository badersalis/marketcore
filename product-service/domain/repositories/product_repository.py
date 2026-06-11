from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Product]:
        pass

    @abstractmethod
    async def count(self, category_id: Optional[str] = None, active_only: bool = True) -> int:
        pass

    @abstractmethod
    async def save(self, product: Product) -> Product:
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        pass


__all__ = ["ProductRepository"]
