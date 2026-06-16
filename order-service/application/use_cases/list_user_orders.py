from typing import List

from application.dtos.order_dtos import OrderResponse
from application.use_cases.place_order import _to_order_response
from domain.repositories.order_repository import OrderRepository


class ListUserOrders:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    async def execute(self, user_id: str, skip: int = 0, limit: int = 20) -> List[OrderResponse]:
        orders = await self._order_repo.list_by_user(user_id, skip=skip, limit=limit)
        return [_to_order_response(o) for o in orders]


__all__ = ["ListUserOrders"]
