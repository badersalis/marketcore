import json
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.order import Order, OrderItem
from domain.repositories.order_repository import OrderRepository
from domain.value_objects.money import Money
from domain.value_objects.order_status import OrderStatus
from domain.value_objects.shipping_address import ShippingAddress
from infrastructure.persistence.models import OrderModel


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _deserialize_items(self, items_json: str) -> list[OrderItem]:
        raw = json.loads(items_json)
        return [
            OrderItem(
                product_id=i["product_id"],
                sku_id=i.get("sku_id"),
                name=i["name"],
                unit_price=Money(amount=Decimal(str(i["unit_price"])), currency=i.get("currency", "USD")),
                quantity=i["quantity"],
            )
            for i in raw
        ]

    def _serialize_items(self, items: list[OrderItem]) -> str:
        return json.dumps([
            {
                "product_id": item.product_id,
                "sku_id": item.sku_id,
                "name": item.name,
                "unit_price": str(item.unit_price.amount),
                "currency": item.unit_price.currency,
                "quantity": item.quantity,
            }
            for item in items
        ])

    def _to_entity(self, model: OrderModel) -> Order:
        total = Money(amount=Decimal(str(model.total_amount)), currency=model.currency)
        shipping = None
        if model.shipping_address_json:
            raw = json.loads(model.shipping_address_json)
            shipping = ShippingAddress(
                full_name=raw["full_name"],
                line1=raw["line1"],
                line2=raw.get("line2"),
                city=raw["city"],
                country=raw["country"],
                postal_code=raw["postal_code"],
            )
        return Order(
            id=model.id,
            user_id=model.user_id,
            status=OrderStatus(model.status) if isinstance(model.status, str) else model.status,
            items=self._deserialize_items(model.items_json),
            total=total,
            shipping_address=shipping,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _serialize_address(self, address: Optional[ShippingAddress]) -> Optional[str]:
        if not address:
            return None
        return json.dumps({
            "full_name": address.full_name,
            "line1": address.line1,
            "line2": address.line2,
            "city": address.city,
            "country": address.country,
            "postal_code": address.postal_code,
        })

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total.amount if order.total else Decimal("0"),
            currency=order.total.currency if order.total else "USD",
            items_json=self._serialize_items(order.items),
            shipping_address_json=self._serialize_address(order.shipping_address),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return order

    async def update(self, order: Order) -> Order:
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.id == order.id)
        )
        model = result.scalar_one()
        model.status = order.status
        model.items_json = self._serialize_items(order.items)
        model.total_amount = order.total.amount if order.total else Decimal("0")
        model.shipping_address_json = self._serialize_address(order.shipping_address)
        model.updated_at = order.updated_at
        await self._session.flush()
        return order


__all__ = ["SQLAlchemyOrderRepository"]
