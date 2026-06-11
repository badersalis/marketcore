from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.product_dtos import (
    CreateProductRequest,
    ProductListResponse,
    ProductResponse,
    UpdateProductRequest,
)
from application.use_cases.create_product import CreateProduct
from application.use_cases.deactivate_product import DeactivateProduct
from application.use_cases.get_product_by_id import GetProductById
from application.use_cases.list_products import ListProducts
from application.use_cases.update_product import UpdateProduct
from domain.exceptions.product_exceptions import CategoryNotFoundException, ProductNotFoundException
from infrastructure.persistence.database import get_db
from infrastructure.repositories.category_repository_impl import SQLAlchemyCategoryRepository
from infrastructure.repositories.product_repository_impl import SQLAlchemyProductRepository

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: CreateProductRequest,
    db: AsyncSession = Depends(get_db),
):
    product_repo = SQLAlchemyProductRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)
    try:
        return await CreateProduct(product_repo, category_repo).execute(request)
    except CategoryNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyProductRepository(db)
    return await ListProducts(repo).execute(skip=skip, limit=limit, category_id=category_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyProductRepository(db)
    try:
        return await GetProductById(repo).execute(product_id)
    except ProductNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    request: UpdateProductRequest,
    db: AsyncSession = Depends(get_db),
):
    product_repo = SQLAlchemyProductRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)
    try:
        return await UpdateProduct(product_repo, category_repo).execute(product_id, request)
    except ProductNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except CategoryNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(product_id: str, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyProductRepository(db)
    try:
        await DeactivateProduct(repo).execute(product_id)
    except ProductNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
