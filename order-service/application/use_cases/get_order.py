from application.dtos.order_dtos import OrderResponse
from application.use_cases.place_order import _to_order_response
from domain.exceptions.order_exceptions import OrderNotFoundException
from domain.repositories.order_repository import OrderRepository
from fastapi import HTTPException


class GetOrder:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    async def execute(self, order_id: str, user_id: str, role: str) -> OrderResponse:
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException(order_id)

        if role != "operator" and order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot view another user's order")

        return _to_order_response(order)


__all__ = ["GetOrder"]
