from typing import List

from application.dtos.product_dtos import CategoryResponse
from domain.repositories.category_repository import CategoryRepository


class ListCategories:
    """Returns all product categories."""

    def __init__(self, category_repo: CategoryRepository) -> None:
        self._repo = category_repo

    async def execute(self) -> List[CategoryResponse]:
        categories = await self._repo.list()
        return [
            CategoryResponse(id=c.id, name=c.name, slug=str(c.slug)) for c in categories
        ]


__all__ = ["ListCategories"]
