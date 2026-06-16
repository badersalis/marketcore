from application.dtos.order_dtos import OrderItemResponse, OrderResponse, PlaceOrderRequest, ShippingAddressDTO
from domain.entities.order import Order, OrderItem
from domain.exceptions.order_exceptions import CartNotFoundException, EmptyCartException
from domain.repositories.cart_repository import CartRepository
from domain.repositories.order_repository import OrderRepository
from domain.value_objects.shipping_address import ShippingAddress
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.order_events import OrderPlaced


class PlaceOrder:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._order_repo = order_repo
        self._cart_repo = cart_repo
        self._event_publisher = event_publisher

    async def execute(self, user_id: str, request: PlaceOrderRequest) -> OrderResponse:
        cart = await self._cart_repo.get_by_user_id(user_id)
        if not cart:
            raise CartNotFoundException(user_id)
        if cart.is_empty:
            raise EmptyCartException()

        addr_dto = request.shipping_address
        shipping = ShippingAddress(
            full_name=addr_dto.full_name,
            line1=addr_dto.line1,
            line2=addr_dto.line2,
            city=addr_dto.city,
            country=addr_dto.country,
            postal_code=addr_dto.postal_code,
        )

        order_items = [
            OrderItem(
                product_id=i.product_id,
                sku_id=i.sku_id,
                name=i.name,
                unit_price=i.unit_price,
                quantity=i.quantity,
            )
            for i in cart.items
        ]
        total = cart.total
        order = Order(
            user_id=user_id,
            items=order_items,
            total=total,
            shipping_address=shipping,
        )
        await self._order_repo.save(order)
        await self._cart_repo.delete(user_id)

        event = OrderPlaced(
            order_id=order.id,
            user_id=user_id,
            items=[
                {"product_id": i.product_id, "sku_id": i.sku_id, "quantity": i.quantity}
                for i in order.items
            ],
            total_amount=str(total.amount),
            currency=total.currency,
        )
        await self._event_publisher.publish("order.events", event)
        return _to_order_response(order)


def _to_order_response(order: Order) -> OrderResponse:
    items = [
        OrderItemResponse(
            product_id=i.product_id,
            sku_id=i.sku_id,
            name=i.name,
            unit_price=str(i.unit_price.amount),
            currency=i.unit_price.currency,
            quantity=i.quantity,
            subtotal=str(i.subtotal.amount),
        )
        for i in order.items
    ]
    addr = None
    if order.shipping_address:
        a = order.shipping_address
        addr = ShippingAddressDTO(
            full_name=a.full_name, line1=a.line1, line2=a.line2,
            city=a.city, country=a.country, postal_code=a.postal_code,
        )
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        items=items,
        total=str(order.total.amount) if order.total else "0.00",
        currency=order.total.currency if order.total else "USD",
        shipping_address=addr,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


__all__ = ["PlaceOrder", "_to_order_response"]
