from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.sku import Sku
from domain.repositories.sku_repository import SkuRepository
from domain.value_objects.money import Money
from infrastructure.persistence.models import SkuModel


class SQLAlchemySkuRepository(SkuRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: SkuModel) -> Sku:
        price = (
            Money(amount=Decimal(str(model.price_amount)), currency=model.price_currency)
            if model.price_amount is not None
            else None
        )
        return Sku(
            id=model.id,
            product_id=model.product_id,
            code=model.code,
            attributes=model.attributes or {},
            price=price,
            stock=model.stock,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    async def get_by_id(self, sku_id: str) -> Optional[Sku]:
        result = await self._session.execute(
            select(SkuModel).where(SkuModel.id == sku_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Optional[Sku]:
        result = await self._session.execute(
            select(SkuModel).where(SkuModel.code == code)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_product(self, product_id: str) -> List[Sku]:
        result = await self._session.execute(
            select(SkuModel)
            .where(SkuModel.product_id == product_id)
            .order_by(SkuModel.created_at.asc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, sku: Sku) -> Sku:
        model = SkuModel(
            id=sku.id,
            product_id=sku.product_id,
            code=sku.code,
            attributes=sku.attributes,
            price_amount=sku.price.amount if sku.price else None,
            price_currency=sku.price.currency if sku.price else None,
            stock=sku.stock,
            is_active=sku.is_active,
            created_at=sku.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return sku

    async def update(self, sku: Sku) -> Sku:
        result = await self._session.execute(
            select(SkuModel).where(SkuModel.id == sku.id)
        )
        model = result.scalar_one()
        model.code = sku.code
        model.attributes = sku.attributes
        model.price_amount = sku.price.amount if sku.price else None
        model.price_currency = sku.price.currency if sku.price else None
        model.stock = sku.stock
        model.is_active = sku.is_active
        await self._session.flush()
        return sku


__all__ = ["SQLAlchemySkuRepository"]
