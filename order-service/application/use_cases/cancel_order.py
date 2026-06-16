from application.dtos.order_dtos import OrderResponse
from application.use_cases.place_order import _to_order_response
from domain.exceptions.order_exceptions import OrderNotFoundException, OrderAlreadyCancelledException
from domain.repositories.order_repository import OrderRepository
from domain.value_objects.role import UserRole
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.order_events import OrderCancelled


class CancelOrder:
    def __init__(self, order_repo: OrderRepository, event_publisher: EventPublisher) -> None:
        self._order_repo = order_repo
        self._event_publisher = event_publisher

    async def execute(self, order_id: str, user_id: str, role: str, reason: str = "") -> OrderResponse:
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException(order_id)

        if role not in ("operator",) and order.user_id != user_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Cannot cancel another user's order")

        order.cancel(reason)
        await self._order_repo.update(order)

        event = OrderCancelled(
            order_id=order.id,
            user_id=order.user_id,
            reason=reason,
            refund_amount=str(order.total.amount) if order.total else "0.00",
        )
        await self._event_publisher.publish("order.events", event)
        return _to_order_response(order)


__all__ = ["CancelOrder"]
