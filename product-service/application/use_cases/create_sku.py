from decimal import Decimal

from application.dtos.product_dtos import CreateSkuRequest, SkuResponse
from domain.entities.sku import Sku
from domain.exceptions.product_exceptions import (
    ProductNotFoundException,
    SkuCodeAlreadyExistsException,
)
from domain.repositories.product_repository import ProductRepository
from domain.repositories.sku_repository import SkuRepository
from domain.value_objects.money import Money


class CreateSku:
    """Creates a new SKU (variant) for an existing product."""

    def __init__(self, product_repo: ProductRepository, sku_repo: SkuRepository) -> None:
        self._product_repo = product_repo
        self._sku_repo = sku_repo

    async def execute(self, product_id: str, request: CreateSkuRequest) -> SkuResponse:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

        existing = await self._sku_repo.get_by_code(request.code)
        if existing:
            raise SkuCodeAlreadyExistsException(request.code)

        price = None
        if request.price is not None:
            currency = request.currency or product.price.currency
            price = Money(amount=Decimal(str(request.price)), currency=currency)

        sku = Sku(
            product_id=product_id,
            code=request.code,
            attributes=request.attributes,
            price=price,
            stock=request.stock,
        )
        sku = await self._sku_repo.save(sku)

        return SkuResponse(
            id=sku.id,
            product_id=sku.product_id,
            code=sku.code,
            attributes=sku.attributes,
            price=sku.price.amount if sku.price else None,
            currency=sku.price.currency if sku.price else None,
            stock=sku.stock,
            is_active=sku.is_active,
            created_at=sku.created_at,
        )


__all__ = ["CreateSku"]
