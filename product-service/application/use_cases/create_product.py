from decimal import Decimal

from application.dtos.product_dtos import CreateProductRequest, ProductResponse
from domain.entities.product import Product
from domain.exceptions.product_exceptions import CategoryNotFoundException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.product_repository import ProductRepository
from domain.value_objects.money import Money


class CreateProduct:
    """Creates a new product in the catalogue under an optional category."""

    def __init__(self, product_repo: ProductRepository, category_repo: CategoryRepository) -> None:
        self._product_repo = product_repo
        self._category_repo = category_repo

    async def execute(self, request: CreateProductRequest) -> ProductResponse:
        if request.category_id:
            category = await self._category_repo.get_by_id(request.category_id)
            if not category:
                raise CategoryNotFoundException(request.category_id)

        product = Product(
            name=request.name,
            description=request.description,
            price=Money(amount=Decimal(str(request.price)), currency=request.currency),
            stock=request.stock,
            category_id=request.category_id,
        )
        product = await self._product_repo.save(product)
        return _to_response(product)


def _to_response(p: Product) -> ProductResponse:
    from application.dtos.product_dtos import ProductResponse
    return ProductResponse(
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


__all__ = ["CreateProduct"]
