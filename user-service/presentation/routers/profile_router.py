from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.user_dtos import ProfileResponse, UpdateProfileRequest
from application.use_cases.get_profile import GetProfile
from application.use_cases.update_profile import UpdateProfile
from infrastructure.persistence.database import get_db
from infrastructure.repositories.profile_repository_impl import SQLAlchemyProfileRepository
from presentation.dependencies.permissions import require_member

router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(
    payload: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    use_case = GetProfile(SQLAlchemyProfileRepository(db))
    return await use_case.execute(user_id=payload["sub"])


@router.put("", response_model=ProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    payload: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    use_case = UpdateProfile(SQLAlchemyProfileRepository(db))
    return await use_case.execute(user_id=payload["sub"], request=body)


__all__ = ["router"]
