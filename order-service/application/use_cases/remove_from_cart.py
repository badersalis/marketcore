from typing import Optional

from application.dtos.order_dtos import CartResponse
from domain.exceptions.order_exceptions import CartNotFoundException
from domain.repositories.cart_repository import CartRepository
from application.use_cases.add_to_cart import _to_cart_response


class RemoveFromCart:
    def __init__(self, cart_repo: CartRepository) -> None:
        self._cart_repo = cart_repo

    async def execute(self, user_id: str, product_id: str, sku_id: Optional[str] = None) -> CartResponse:
        cart = await self._cart_repo.get_by_user_id(user_id)
        if not cart:
            raise CartNotFoundException(user_id)

        cart.remove_item(product_id, sku_id)
        await self._cart_repo.save(cart)
        return _to_cart_response(cart)


__all__ = ["RemoveFromCart"]
