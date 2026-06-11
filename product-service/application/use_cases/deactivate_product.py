from domain.exceptions.product_exceptions import ProductNotFoundException
from domain.repositories.product_repository import ProductRepository


class DeactivateProduct:
    """Soft-deletes a product by marking it inactive."""

    def __init__(self, product_repo: ProductRepository) -> None:
        self._repo = product_repo

    async def execute(self, product_id: str) -> None:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        product.deactivate()
        await self._repo.update(product)


__all__ = ["DeactivateProduct"]
