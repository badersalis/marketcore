from application.dtos.order_dtos import OrderResponse, UpdateOrderStatusRequest
from application.use_cases.place_order import _to_order_response
from domain.exceptions.order_exceptions import OrderNotFoundException, InvalidOrderStatusTransitionException
from domain.repositories.order_repository import OrderRepository


class UpdateOrderStatus:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    async def execute(self, order_id: str, request: UpdateOrderStatusRequest) -> OrderResponse:
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException(order_id)

        order.transition_to(request.status)
        await self._order_repo.update(order)
        return _to_order_response(order)


__all__ = ["UpdateOrderStatus"]
