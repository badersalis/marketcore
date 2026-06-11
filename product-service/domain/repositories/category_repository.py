from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Category]:
        pass

    @abstractmethod
    async def list(self) -> List[Category]:
        pass

    @abstractmethod
    async def save(self, category: Category) -> Category:
        pass


__all__ = ["CategoryRepository"]
