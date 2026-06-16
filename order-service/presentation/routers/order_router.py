from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.order_dtos import OrderResponse, PlaceOrderRequest, UpdateOrderStatusRequest
from application.use_cases.cancel_order import CancelOrder
from application.use_cases.get_order import GetOrder
from application.use_cases.list_user_orders import ListUserOrders
from application.use_cases.place_order import PlaceOrder
from application.use_cases.update_order_status import UpdateOrderStatus
from domain.exceptions.order_exceptions import (
    CartNotFoundException,
    EmptyCartException,
    InvalidOrderStatusTransitionException,
    OrderAlreadyCancelledException,
    OrderNotFoundException,
)
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import get_db
from infrastructure.repositories.cart_repository_impl import HybridCartRepository
from infrastructure.repositories.order_repository_impl import SQLAlchemyOrderRepository
from presentation.dependencies.permissions import require_member, require_operator

router = APIRouter()


def _publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


def _redis(request: Request):
    return request.app.state.redis


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    body: PlaceOrderRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> OrderResponse:
    use_case = PlaceOrder(
        order_repo=SQLAlchemyOrderRepository(db),
        cart_repo=HybridCartRepository(redis=_redis(request), session=db),
        event_publisher=_publisher(request),
    )
    try:
        return await use_case.execute(current_user["sub"], body)
    except (CartNotFoundException, EmptyCartException) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> List[OrderResponse]:
    return await ListUserOrders(SQLAlchemyOrderRepository(db)).execute(
        current_user["sub"], skip=skip, limit=limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> OrderResponse:
    try:
        return await GetOrder(SQLAlchemyOrderRepository(db)).execute(
            order_id, current_user["sub"], current_user.get("role", "member")
        )
    except OrderNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete("/{order_id}", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> OrderResponse:
    use_case = CancelOrder(
        order_repo=SQLAlchemyOrderRepository(db),
        event_publisher=_publisher(request),
    )
    try:
        return await use_case.execute(
            order_id,
            user_id=current_user["sub"],
            role=current_user.get("role", "member"),
        )
    except OrderNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except OrderAlreadyCancelledException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    body: UpdateOrderStatusRequest,
    db: AsyncSession = Depends(get_db),
    operator: dict = Depends(require_operator),
) -> OrderResponse:
    try:
        return await UpdateOrderStatus(SQLAlchemyOrderRepository(db)).execute(order_id, body)
    except OrderNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except InvalidOrderStatusTransitionException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


__all__ = ["router"]
