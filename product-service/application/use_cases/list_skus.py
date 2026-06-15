from typing import List

from application.dtos.product_dtos import SkuResponse
from domain.exceptions.product_exceptions import ProductNotFoundException
from domain.repositories.product_repository import ProductRepository
from domain.repositories.sku_repository import SkuRepository


class ListSkus:
    """Returns all SKUs for a product."""

    def __init__(self, product_repo: ProductRepository, sku_repo: SkuRepository) -> None:
        self._product_repo = product_repo
        self._sku_repo = sku_repo

    async def execute(self, product_id: str) -> List[SkuResponse]:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

        skus = await self._sku_repo.list_by_product(product_id)
        return [
            SkuResponse(
                id=s.id,
                product_id=s.product_id,
                code=s.code,
                attributes=s.attributes,
                price=s.price.amount if s.price else None,
                currency=s.price.currency if s.price else None,
                stock=s.stock,
                is_active=s.is_active,
                created_at=s.created_at,
            )
            for s in skus
        ]


__all__ = ["ListSkus"]
