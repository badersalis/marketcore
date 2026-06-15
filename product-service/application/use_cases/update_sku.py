from decimal import Decimal

from application.dtos.product_dtos import SkuResponse, UpdateSkuRequest
from domain.exceptions.product_exceptions import SkuCodeAlreadyExistsException, SkuNotFoundException
from domain.repositories.sku_repository import SkuRepository
from domain.value_objects.money import Money


class UpdateSku:
    """Updates mutable fields on an existing SKU."""

    def __init__(self, sku_repo: SkuRepository) -> None:
        self._sku_repo = sku_repo

    async def execute(self, sku_id: str, request: UpdateSkuRequest) -> SkuResponse:
        sku = await self._sku_repo.get_by_id(sku_id)
        if not sku:
            raise SkuNotFoundException(sku_id)

        if request.code is not None and request.code != sku.code:
            existing = await self._sku_repo.get_by_code(request.code)
            if existing:
                raise SkuCodeAlreadyExistsException(request.code)
            sku.code = request.code.strip().upper()

        if request.attributes is not None:
            sku.attributes = request.attributes

        if request.stock is not None:
            sku.stock = request.stock

        if request.price is not None:
            currency = request.currency or (sku.price.currency if sku.price else "USD")
            sku.price = Money(amount=Decimal(str(request.price)), currency=currency)
        elif request.currency is not None and sku.price is not None:
            sku.price = Money(amount=sku.price.amount, currency=request.currency)

        sku = await self._sku_repo.update(sku)

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


__all__ = ["UpdateSku"]
