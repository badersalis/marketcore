import asyncio
import json
import logging
from decimal import Decimal
from typing import Optional

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.cart import Cart, CartItem
from domain.repositories.cart_repository import CartRepository
from domain.value_objects.money import Money
from infrastructure.cache.redis_client import CART_TTL_AUTHENTICATED
from infrastructure.persistence.database import AsyncSessionFactory
from infrastructure.persistence.models import CartModel

logger = logging.getLogger(__name__)

_CART_KEY = "cart:{user_id}"


def _cart_key(user_id: str) -> str:
    return f"cart:{user_id}"


def _serialize(cart: Cart) -> str:
    return json.dumps({
        "id": cart.id,
        "user_id": cart.user_id,
        "items": [
            {
                "product_id": i.product_id,
                "sku_id": i.sku_id,
                "name": i.name,
                "unit_price": str(i.unit_price.amount),
                "currency": i.unit_price.currency,
                "quantity": i.quantity,
            }
            for i in cart.items
        ],
        "created_at": cart.created_at.isoformat(),
        "updated_at": cart.updated_at.isoformat(),
    })


def _deserialize(raw: str, cart_id: str = "") -> Cart:
    from datetime import datetime
    data = json.loads(raw)
    items = [
        CartItem(
            product_id=i["product_id"],
            sku_id=i.get("sku_id"),
            name=i["name"],
            unit_price=Money(amount=Decimal(i["unit_price"]), currency=i.get("currency", "USD")),
            quantity=i["quantity"],
        )
        for i in data.get("items", [])
    ]
    return Cart(
        id=data.get("id", cart_id),
        user_id=data["user_id"],
        items=items,
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


async def _sync_to_db(cart: Cart) -> None:
    """Background task: persist cart to PostgreSQL after Redis write."""
    try:
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(CartModel).where(CartModel.user_id == cart.user_id)
            )
            model = result.scalar_one_or_none()
            items_json = json.dumps([
                {
                    "product_id": i.product_id,
                    "sku_id": i.sku_id,
                    "name": i.name,
                    "unit_price": str(i.unit_price.amount),
                    "currency": i.unit_price.currency,
                    "quantity": i.quantity,
                }
                for i in cart.items
            ])
            if model:
                model.items_json = items_json
                model.updated_at = cart.updated_at
            else:
                model = CartModel(
                    id=cart.id,
                    user_id=cart.user_id,
                    items_json=items_json,
                    created_at=cart.created_at,
                    updated_at=cart.updated_at,
                )
                session.add(model)
            await session.commit()
    except Exception as exc:
        logger.error("Background cart DB sync failed for user %s: %s", cart.user_id, exc)


async def _delete_from_db(user_id: str) -> None:
    try:
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(CartModel).where(CartModel.user_id == user_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
    except Exception as exc:
        logger.error("Background cart DB delete failed for user %s: %s", user_id, exc)


class HybridCartRepository(CartRepository):
    """Read from Redis first; fall back to PostgreSQL on cache miss.
    Writes hit Redis immediately; DB persistence is fired as a background task."""

    def __init__(self, redis: aioredis.Redis, session: AsyncSession) -> None:
        self._redis = redis
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        cached = await self._redis.get(_cart_key(user_id))
        if cached:
            return _deserialize(cached)

        result = await self._session.execute(
            select(CartModel).where(CartModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        items = [
            CartItem(
                product_id=i["product_id"],
                sku_id=i.get("sku_id"),
                name=i["name"],
                unit_price=Money(amount=Decimal(i["unit_price"]), currency=i.get("currency", "USD")),
                quantity=i["quantity"],
            )
            for i in json.loads(model.items_json)
        ]
        from datetime import datetime
        cart = Cart(
            id=model.id,
            user_id=model.user_id,
            items=items,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        await self._redis.setex(_cart_key(user_id), CART_TTL_AUTHENTICATED, _serialize(cart))
        return cart

    async def save(self, cart: Cart) -> Cart:
        await self._redis.setex(_cart_key(cart.user_id), CART_TTL_AUTHENTICATED, _serialize(cart))
        asyncio.create_task(_sync_to_db(cart))
        return cart

    async def delete(self, user_id: str) -> None:
        await self._redis.delete(_cart_key(user_id))
        asyncio.create_task(_delete_from_db(user_id))


__all__ = ["HybridCartRepository"]
