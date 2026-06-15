from datetime import datetime, timedelta, timezone

from application.dtos.auth_dtos import LoginRequest, TokenResponse
from application.services.token_service import TokenService
from core.config import settings
from domain.entities.refresh_token import RefreshToken
from domain.exceptions.auth_exceptions import InvalidCredentialsException
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository


class LoginUser:
    """Authenticates a user with email + password and returns JWT access and refresh tokens."""

    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._token_service = token_service

    async def execute(self, request: LoginRequest) -> TokenResponse:
        user = await self._user_repo.get_by_email(request.email)
        if not user or not user.is_active:
            raise InvalidCredentialsException()

        if not user.hashed_password.verify(request.password):
            raise InvalidCredentialsException()

        access_token = self._token_service.create_access_token(user.id)
        refresh_token_value = self._token_service.create_refresh_token_value()

        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_value,
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self._token_repo.save(refresh_token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


__all__ = ["LoginUser"]
