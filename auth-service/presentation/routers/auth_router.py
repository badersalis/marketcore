from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.auth_dtos import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from application.services.token_service import TokenService
from application.use_cases.login_user import LoginUser
from application.use_cases.logout_user import LogoutUser
from application.use_cases.refresh_access_token import RefreshAccessToken
from application.use_cases.register_user import RegisterUser
from domain.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
)
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import get_db
from infrastructure.repositories.refresh_token_repository_impl import (
    SQLAlchemyRefreshTokenRepository,
)
from infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository

router = APIRouter()
_security = HTTPBearer()
_token_service = TokenService()


def _publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(_publisher),
) -> UserResponse:
    use_case = RegisterUser(
        user_repo=SQLAlchemyUserRepository(db),
        event_publisher=publisher,
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
        created_at=user.created_at,
    )


__all__ = ["router"]
