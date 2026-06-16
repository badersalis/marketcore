from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.auth_dtos import AssignRoleRequest, UserResponse
from application.use_cases.approve_merchant import ApproveMerchant
from application.use_cases.assign_operator import AssignOperator
from domain.exceptions.auth_exceptions import UserNotFoundException
from domain.value_objects.role import UserRole
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import get_db
from infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository
from presentation.dependencies.permissions import require_operator

router = APIRouter()


def _publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


@router.post(
    "/merchant-requests/{request_id}/approve",
    status_code=status.HTTP_200_OK,
    summary="Approve a pending merchant upgrade request",
)
async def approve_merchant_request(
    request_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(_publisher),
    operator: dict = Depends(require_operator),
) -> dict:
    use_case = ApproveMerchant(
        user_repo=SQLAlchemyUserRepository(db),
        event_publisher=publisher,
        session=db,
    )
    try:
        return await use_case.execute(request_id, reviewer_id=operator["sub"])
    except UserNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/assign-role",
    status_code=status.HTTP_200_OK,
    summary="Assign operator role to a user",
)
async def assign_operator_role(
    body: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    operator: dict = Depends(require_operator),
) -> dict:
    if body.role != UserRole.OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only assigns the operator role",
        )
    use_case = AssignOperator(user_repo=SQLAlchemyUserRepository(db))
    try:
        return await use_case.execute(body.user_id)
    except UserNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


__all__ = ["router"]
