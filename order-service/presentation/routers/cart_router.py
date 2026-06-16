from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.order_dtos import AddToCartRequest, CartResponse
from application.use_cases.add_to_cart import AddToCart
from application.use_cases.get_cart import GetCart
from application.use_cases.remove_from_cart import RemoveFromCart
from domain.exceptions.order_exceptions import CartNotFoundException, InsufficientStockException
from infrastructure.clients.product_client import ProductServiceClient
from infrastructure.persistence.database import get_db
from infrastructure.repositories.cart_repository_impl import HybridCartRepository
from presentation.dependencies.permissions import require_member

router = APIRouter()
_product_client = ProductServiceClient()


def _redis(request: Request):
    return request.app.state.redis


@router.post("", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def add_to_cart(
    body: AddToCartRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> CartResponse:
    cart_repo = HybridCartRepository(redis=_redis(request), session=db)
    use_case = AddToCart(cart_repo=cart_repo, product_client=_product_client)
    try:
        return await use_case.execute(current_user["sub"], body)
    except InsufficientStockException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.delete("/{product_id}", response_model=CartResponse)
async def remove_from_cart(
    product_id: str,
    sku_id: Optional[str] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> CartResponse:
    cart_repo = HybridCartRepository(redis=_redis(request), session=db)
    use_case = RemoveFromCart(cart_repo=cart_repo)
    try:
        return await use_case.execute(current_user["sub"], product_id, sku_id)
    except CartNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("", response_model=CartResponse)
async def get_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_member),
) -> CartResponse:
    cart_repo = HybridCartRepository(redis=_redis(request), session=db)
    return await GetCart(cart_repo=cart_repo).execute(current_user["sub"])


__all__ = ["router"]
