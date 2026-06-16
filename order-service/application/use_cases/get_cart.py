from application.dtos.order_dtos import CartResponse
from domain.entities.cart import Cart
from domain.repositories.cart_repository import CartRepository
from application.use_cases.add_to_cart import _to_cart_response
from decimal import Decimal
from domain.value_objects.money import Money


class GetCart:
    def __init__(self, cart_repo: CartRepository) -> None:
        self._cart_repo = cart_repo

    async def execute(self, user_id: str) -> CartResponse:
        cart = await self._cart_repo.get_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
        return _to_cart_response(cart)


__all__ = ["GetCart"]
