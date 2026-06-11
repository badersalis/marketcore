from application.dtos.product_dtos import CreateCategoryRequest, CategoryResponse
from domain.entities.category import Category
from domain.exceptions.product_exceptions import SlugAlreadyExistsException
from domain.repositories.category_repository import CategoryRepository
from domain.value_objects.slug import Slug


class CreateCategory:
    """Creates a new product category and ensures its slug is unique."""

    def __init__(self, category_repo: CategoryRepository) -> None:
        self._repo = category_repo

    async def execute(self, request: CreateCategoryRequest) -> CategoryResponse:
        slug = Slug.from_string(request.name)
        existing = await self._repo.get_by_slug(str(slug))
        if existing:
            raise SlugAlreadyExistsException(str(slug))

        category = Category(name=request.name, slug=slug)
        category = await self._repo.save(category)

        return CategoryResponse(id=category.id, name=category.name, slug=str(category.slug))


__all__ = ["CreateCategory"]
