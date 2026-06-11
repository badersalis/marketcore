from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.category import Category
from domain.repositories.category_repository import CategoryRepository
from domain.value_objects.slug import Slug
from infrastructure.persistence.models import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(id=model.id, name=model.name, slug=Slug(model.slug))

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self) -> List[Category]:
        result = await self._session.execute(select(CategoryModel))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, category: Category) -> Category:
        model = CategoryModel(id=category.id, name=category.name, slug=str(category.slug))
        self._session.add(model)
        await self._session.flush()
        return category


__all__ = ["SQLAlchemyCategoryRepository"]
