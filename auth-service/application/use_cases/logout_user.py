from application.dtos.auth_dtos import RefreshRequest
from domain.repositories.refresh_token_repository import RefreshTokenRepository


class LogoutUser:
    """Revokes the user's refresh token, invalidating their session."""

    def __init__(self, token_repo: RefreshTokenRepository) -> None:
        self._token_repo = token_repo

    async def execute(self, request: RefreshRequest) -> None:
        await self._token_repo.revoke(request.refresh_token)


__all__ = ["LogoutUser"]
