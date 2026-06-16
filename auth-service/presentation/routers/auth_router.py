from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.auth_dtos import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    SendVerificationRequest,
    TokenResponse,
    UserResponse,
    VerifyOtpRequest,
)
from application.services.otp_service import OtpService
from application.services.token_service import TokenService
from application.use_cases.login_user import LoginUser
from application.use_cases.logout_user import LogoutUser
from application.use_cases.refresh_access_token import RefreshAccessToken
from application.use_cases.register_user import RegisterUser
from application.use_cases.request_merchant_upgrade import RequestMerchantUpgrade
from application.use_cases.send_verification_email import SendVerificationEmail
from application.use_cases.verify_email import VerifyEmail
from domain.exceptions.auth_exceptions import (
    EmailAlreadyVerifiedException,
    InvalidCredentialsException,
    InvalidOtpException,
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from domain.value_objects.role import UserRole
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import get_db
from infrastructure.repositories.refresh_token_repository_impl import (
    SQLAlchemyRefreshTokenRepository,
)
from infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository
from presentation.dependencies.permissions import require_member

router = APIRouter()
_security = HTTPBearer()
_token_service = TokenService()


def _publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


def _redis(request: Request) -> Redis:
    return request.app.state.redis


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(_publisher),
    redis: Redis = Depends(_redis),
) -> UserResponse:
    use_case = RegisterUser(
        user_repo=SQLAlchemyUserRepository(db),
        event_publisher=publisher,
        otp_service=OtpService(redis),
    )
    try:
        return await use_case.execute(body)
    except UserAlreadyExistsException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    use_case = LoginUser(
        user_repo=SQLAlchemyUserRepository(db),
        token_repo=SQLAlchemyRefreshTokenRepository(db),
        token_service=_token_service,
    )
    try:
        return await use_case.execute(body)
    except InvalidCredentialsException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    use_case = RefreshAccessToken(
        user_repo=SQLAlchemyUserRepository(db),
        token_repo=SQLAlchemyRefreshTokenRepository(db),
        token_service=_token_service,
    )
    try:
        return await use_case.execute(body)
    except InvalidTokenException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> None:
    use_case = LogoutUser(token_repo=SQLAlchemyRefreshTokenRepository(db))
    await use_case.execute(body)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user_id = _token_service.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    repo = SQLAlchemyUserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        id=user.id,
        email=str(user.email),
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        is_merchant_approved=user.is_merchant_approved,
        created_at=user.created_at,
    )


@router.post(
    "/send-verification",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a new OTP verification email",
    description=(
        "Generates a fresh 6-digit OTP and sends it to the given address. "
        "Always returns 202 — even when the email is not registered — "
        "to avoid leaking account existence."
    ),
)
async def send_verification(
    body: SendVerificationRequest,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(_publisher),
    redis: Redis = Depends(_redis),
) -> dict:
    use_case = SendVerificationEmail(
        user_repo=SQLAlchemyUserRepository(db),
        otp_service=OtpService(redis),
        event_publisher=publisher,
    )
    try:
        await use_case.execute(body.email)
    except EmailAlreadyVerifiedException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    return {"detail": "If that address is registered and unverified, a verification email has been sent."}


@router.post(
    "/verify-email",
    response_model=UserResponse,
    summary="Verify email address with OTP",
    description="Submit the 6-digit OTP received by email to confirm the account.",
)
async def verify_email(
    body: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(_redis),
    publisher: EventPublisher = Depends(_publisher),
) -> UserResponse:
    use_case = VerifyEmail(
        user_repo=SQLAlchemyUserRepository(db),
        otp_service=OtpService(redis),
        event_publisher=publisher,
    )
    try:
        return await use_case.execute(body.email, body.otp)
    except InvalidOtpException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except EmailAlreadyVerifiedException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/merchant-upgrade",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request upgrade from member to merchant role",
)
async def request_merchant_upgrade(
    request: Request,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(_publisher),
    current_user: dict = Depends(require_member),
) -> dict:
    use_case = RequestMerchantUpgrade(
        user_repo=SQLAlchemyUserRepository(db),
        event_publisher=publisher,
        session=db,
    )
    try:
        return await use_case.execute(current_user["sub"])
    except UserNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


__all__ = ["router"]
