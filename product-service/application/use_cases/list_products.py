from typing import Optional

from application.dtos.product_dtos import ProductListResponse, ProductResponse
from domain.repositories.product_repository import ProductRepository


class ListProducts:
    """Returns a paginated list of active products, optionally filtered by category."""

    def __init__(self, product_repo: ProductRepository) -> None:
        self._repo = product_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[str] = None,
    ) -> ProductListResponse:
        products = await self._repo.list(skip=skip, limit=limit, category_id=category_id)
        total = await self._repo.count(category_id=category_id)

        items = [
            ProductResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                price=p.price.amount,
                currency=p.price.currency,
                stock=p.stock,
                category_id=p.category_id,
                is_active=p.is_active,
                created_at=p.created_at,
            )
            for p in products
        ]
        return ProductListResponse(items=items, total=total, skip=skip, limit=limit)


__all__ = ["ListProducts"]
