from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.product import Product
from domain.repositories.product_repository import ProductRepository
from domain.value_objects.money import Money
from infrastructure.persistence.models import ProductModel


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: ProductModel) -> Product:
        from domain.entities.product import ProductStatus
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=Money(amount=Decimal(str(model.price_amount)), currency=model.price_currency),
            stock=model.stock,
            category_id=model.category_id,
            is_active=model.is_active,
            status=ProductStatus(model.status) if isinstance(model.status, str) else model.status,
            image_urls=model.image_urls or [],
            created_at=model.created_at,
        )

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Product]:
        q = select(ProductModel)
        if active_only:
            q = q.where(ProductModel.is_active.is_(True))
        if category_id:
            q = q.where(ProductModel.category_id == category_id)
        q = q.offset(skip).limit(limit).order_by(ProductModel.created_at.desc())
        result = await self._session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count(self, category_id: Optional[str] = None, active_only: bool = True) -> int:
        q = select(func.count()).select_from(ProductModel)
        if active_only:
            q = q.where(ProductModel.is_active.is_(True))
        if category_id:
            q = q.where(ProductModel.category_id == category_id)
        result = await self._session.execute(q)
        return result.scalar_one()

    async def save(self, product: Product) -> Product:
        model = ProductModel(
            id=product.id,
            name=product.name,
            description=product.description,
            price_amount=product.price.amount,
            price_currency=product.price.currency,
            stock=product.stock,
            category_id=product.category_id,
            is_active=product.is_active,
            status=product.status,
            image_urls=product.image_urls,
            created_at=product.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return product

    async def update(self, product: Product) -> Product:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product.id)
        )
        model = result.scalar_one()
        model.name = product.name
        model.description = product.description
        model.price_amount = product.price.amount
        model.price_currency = product.price.currency
        model.stock = product.stock
        model.category_id = product.category_id
        model.is_active = product.is_active
        model.status = product.status
        model.image_urls = product.image_urls
        await self._session.flush()
        return product


__all__ = ["SQLAlchemyProductRepository"]
