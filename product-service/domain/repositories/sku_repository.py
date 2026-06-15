from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.sku import Sku


class SkuRepository(ABC):
    @abstractmethod
    async def get_by_id(self, sku_id: str) -> Optional[Sku]:
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Sku]:
        pass

    @abstractmethod
    async def list_by_product(self, product_id: str) -> List[Sku]:
        pass

    @abstractmethod
    async def save(self, sku: Sku) -> Sku:
        pass

    @abstractmethod
    async def update(self, sku: Sku) -> Sku:
        pass


__all__ = ["SkuRepository"]
