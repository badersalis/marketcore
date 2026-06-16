from decimal import Decimal

from application.dtos.order_dtos import AddToCartRequest, CartResponse
from domain.entities.cart import Cart, CartItem
from domain.exceptions.order_exceptions import InsufficientStockException
from domain.repositories.cart_repository import CartRepository
from domain.value_objects.money import Money
from infrastructure.clients.product_client import ProductServiceClient


class AddToCart:
    def __init__(self, cart_repo: CartRepository, product_client: ProductServiceClient) -> None:
        self._cart_repo = cart_repo
        self._product_client = product_client

    async def execute(self, user_id: str, request: AddToCartRequest) -> CartResponse:
        stock_info = await self._product_client.check_stock(
            request.product_id, request.sku_id, request.quantity
        )
        if not stock_info["available"]:
            raise InsufficientStockException(
                request.product_id, request.quantity, stock_info["stock"]
            )

        cart = await self._cart_repo.get_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id)

        price_str = stock_info.get("price", "0") or "0"
        unit_price = Money(amount=Decimal(str(price_str)), currency="USD")
        item = CartItem(
            product_id=request.product_id,
            sku_id=request.sku_id,
            name=stock_info.get("name", ""),
            unit_price=unit_price,
            quantity=request.quantity,
        )
        cart.add_item(item)
        await self._cart_repo.save(cart)

        return _to_cart_response(cart)


def _to_cart_response(cart: Cart) -> CartResponse:
    from application.dtos.order_dtos import CartItemResponse
    items = [
        CartItemResponse(
            product_id=i.product_id,
            sku_id=i.sku_id,
            name=i.name,
            unit_price=str(i.unit_price.amount),
            currency=i.unit_price.currency,
            quantity=i.quantity,
            subtotal=str(i.subtotal.amount),
        )
        for i in cart.items
    ]
    total = cart.total
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items,
        total=str(total.amount),
        currency=total.currency,
    )


__all__ = ["AddToCart"]
