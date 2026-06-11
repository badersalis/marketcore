from decimal import Decimal

from application.dtos.product_dtos import UpdateProductRequest, ProductResponse
from domain.exceptions.product_exceptions import ProductNotFoundException, CategoryNotFoundException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.product_repository import ProductRepository
from domain.value_objects.money import Money


class UpdateProduct:
    """Updates mutable fields of an existing product."""

    def __init__(self, product_repo: ProductRepository, category_repo: CategoryRepository) -> None:
        self._product_repo = product_repo
        self._category_repo = category_repo

    async def execute(self, product_id: str, request: UpdateProductRequest) -> ProductResponse:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

        if request.category_id is not None:
            category = await self._category_repo.get_by_id(request.category_id)
            if not category:
                raise CategoryNotFoundException(request.category_id)
            product.category_id = request.category_id

        if request.name is not None:
            product.name = request.name
        if request.description is not None:
            product.description = request.description
        if request.stock is not None:
            product.stock = request.stock
        if request.price is not None:
            currency = request.currency or product.price.currency
            product.price = Money(amount=Decimal(str(request.price)), currency=currency)

        product = await self._product_repo.update(product)
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock,
            category_id=product.category_id,
            is_active=product.is_active,
            created_at=product.created_at,
        )


__all__ = ["UpdateProduct"]
