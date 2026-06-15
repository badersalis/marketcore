from domain.exceptions.product_exceptions import SkuNotFoundException
from domain.repositories.sku_repository import SkuRepository


class DeactivateSku:
    """Soft-deletes a SKU by marking it inactive."""

    def __init__(self, sku_repo: SkuRepository) -> None:
        self._sku_repo = sku_repo

    async def execute(self, sku_id: str) -> None:
        sku = await self._sku_repo.get_by_id(sku_id)
        if not sku:
            raise SkuNotFoundException(sku_id)
        sku.deactivate()
        await self._sku_repo.update(sku)


__all__ = ["DeactivateSku"]
