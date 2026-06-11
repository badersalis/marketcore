from application.dtos.auth_dtos import RefreshRequest, TokenResponse
from application.services.token_service import TokenService
from domain.exceptions.auth_exceptions import InvalidTokenException
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository


class RefreshAccessToken:
    """Issues a new access token if the provided refresh token is valid and not expired."""

    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._token_service = token_service

    async def execute(self, request: RefreshRequest) -> TokenResponse:
        token = await self._token_repo.get_by_token(request.refresh_token)
        if not token or token.is_revoked or token.is_expired:
            raise InvalidTokenException("refresh token is invalid or expired")

        user = await self._user_repo.get_by_id(token.user_id)
        if not user or not user.is_active:
            raise InvalidTokenException("user not found or inactive")

        new_access_token = self._token_service.create_access_token(user.id)
        return TokenResponse(access_token=new_access_token, refresh_token=request.refresh_token)


__all__ = ["RefreshAccessToken"]
