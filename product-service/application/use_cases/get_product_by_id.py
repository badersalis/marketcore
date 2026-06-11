from application.dtos.product_dtos import ProductResponse
from domain.exceptions.product_exceptions import ProductNotFoundException
from domain.repositories.product_repository import ProductRepository


class GetProductById:
    """Retrieves a single product by its ID."""

    def __init__(self, product_repo: ProductRepository) -> None:
        self._repo = product_repo

    async def execute(self, product_id: str) -> ProductResponse:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

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


__all__ = ["GetProductById"]
