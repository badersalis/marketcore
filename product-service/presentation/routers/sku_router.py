from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.product_dtos import CreateSkuRequest, SkuResponse, UpdateSkuRequest
from application.use_cases.create_sku import CreateSku
from application.use_cases.deactivate_sku import DeactivateSku
from application.use_cases.list_skus import ListSkus
from application.use_cases.update_sku import UpdateSku
from domain.exceptions.product_exceptions import (
    ProductNotFoundException,
    SkuCodeAlreadyExistsException,
    SkuNotFoundException,
)
from infrastructure.persistence.database import get_db
from infrastructure.repositories.product_repository_impl import SQLAlchemyProductRepository
from infrastructure.repositories.sku_repository_impl import SQLAlchemySkuRepository

router = APIRouter()


def _repos(db: AsyncSession):
    return SQLAlchemyProductRepository(db), SQLAlchemySkuRepository(db)


@router.post(
    "/",
    response_model=SkuResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a SKU for a product",
)
async def create_sku(
    product_id: str,
    request: CreateSkuRequest,
    db: AsyncSession = Depends(get_db),
):
    product_repo, sku_repo = _repos(db)
    try:
        return await CreateSku(product_repo, sku_repo).execute(product_id, request)
    except ProductNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SkuCodeAlreadyExistsException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.get(
    "/",
    response_model=List[SkuResponse],
    summary="List all SKUs for a product",
)
async def list_skus(product_id: str, db: AsyncSession = Depends(get_db)):
    product_repo, sku_repo = _repos(db)
    try:
        return await ListSkus(product_repo, sku_repo).execute(product_id)
    except ProductNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.put(
    "/{sku_id}",
    response_model=SkuResponse,
    summary="Update a SKU",
)
async def update_sku(
    sku_id: str,
    request: UpdateSkuRequest,
    db: AsyncSession = Depends(get_db),
):
    _, sku_repo = _repos(db)
    try:
        return await UpdateSku(sku_repo).execute(sku_id, request)
    except SkuNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SkuCodeAlreadyExistsException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.delete(
    "/{sku_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a SKU",
)
async def deactivate_sku(sku_id: str, db: AsyncSession = Depends(get_db)):
    _, sku_repo = _repos(db)
    try:
        await DeactivateSku(sku_repo).execute(sku_id)
    except SkuNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


__all__ = ["router"]
