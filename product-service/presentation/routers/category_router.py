from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.product_dtos import CategoryResponse, CreateCategoryRequest
from application.use_cases.create_category import CreateCategory
from application.use_cases.list_categories import ListCategories
from domain.exceptions.product_exceptions import SlugAlreadyExistsException
from infrastructure.persistence.database import get_db
from infrastructure.repositories.category_repository_impl import SQLAlchemyCategoryRepository

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CreateCategoryRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryRepository(db)
    try:
        return await CreateCategory(repo).execute(request)
    except SlugAlreadyExistsException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyCategoryRepository(db)
    return await ListCategories(repo).execute()
