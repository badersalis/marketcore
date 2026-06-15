from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.payment_dtos import (
    ConfirmPaymentRequest,
    CreatePaymentIntentRequest,
    PaymentListResponse,
    PaymentResponse,
)
from application.use_cases.confirm_payment import ConfirmPayment
from application.use_cases.create_payment_intent import CreatePaymentIntent
from application.use_cases.get_payment_status import GetPaymentStatus, ListUserPayments
from domain.exceptions.payment_exceptions import (
    DuplicateIdempotencyKeyException,
    InvalidPaymentTransitionException,
    PaymentNotFoundException,
    UnauthorizedPaymentAccessException,
)
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import get_db
from infrastructure.repositories.payment_repository_impl import SQLAlchemyPaymentRepository

router = APIRouter()
_security = HTTPBearer()


def _publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


def _repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyPaymentRepository:
    return SQLAlchemyPaymentRepository(db)


@router.post(
    "/intents",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a payment intent",
    description=(
        "Initiates a new payment in PENDING state. "
        "Idempotent: submitting the same `idempotency_key` with identical parameters "
        "returns the existing payment without creating a duplicate."
    ),
)
async def create_payment_intent(
    body: CreatePaymentIntentRequest,
    repo: SQLAlchemyPaymentRepository = Depends(_repo),
    publisher: EventPublisher = Depends(_publisher),
) -> PaymentResponse:
    use_case = CreatePaymentIntent(payment_repo=repo, event_publisher=publisher)
    try:
        return await use_case.execute(body)
    except DuplicateIdempotencyKeyException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/{payment_id}/confirm",
    response_model=PaymentResponse,
    summary="Confirm a payment (mock)",
    description=(
        "Moves the payment to CONFIRMED and publishes PaymentConfirmed. "
        "In the stub phase a synthetic provider reference is generated. "
        "Pass the `user_id` of the payment owner as a query parameter for authorization."
    ),
)
async def confirm_payment(
    payment_id: str,
    user_id: str = Query(..., description="ID of the user who owns the payment"),
    body: ConfirmPaymentRequest = Depends(),
    repo: SQLAlchemyPaymentRepository = Depends(_repo),
    publisher: EventPublisher = Depends(_publisher),
) -> PaymentResponse:
    use_case = ConfirmPayment(payment_repo=repo, event_publisher=publisher)
    try:
        return await use_case.execute(payment_id, requesting_user_id=user_id)
    except PaymentNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except UnauthorizedPaymentAccessException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except InvalidPaymentTransitionException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment status",
)
async def get_payment(
    payment_id: str,
    user_id: str = Query(..., description="ID of the requesting user (authorization)"),
    repo: SQLAlchemyPaymentRepository = Depends(_repo),
) -> PaymentResponse:
    use_case = GetPaymentStatus(payment_repo=repo)
    try:
        return await use_case.execute(payment_id, requesting_user_id=user_id)
    except PaymentNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except UnauthorizedPaymentAccessException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.get(
    "/",
    response_model=PaymentListResponse,
    summary="List payments for a user",
)
async def list_payments(
    user_id: str = Query(..., description="Filter payments by this user ID"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    repo: SQLAlchemyPaymentRepository = Depends(_repo),
) -> PaymentListResponse:
    use_case = ListUserPayments(payment_repo=repo)
    return await use_case.execute(user_id=user_id, offset=offset, limit=limit)


__all__ = ["router"]
