from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.refresh_token import RefreshToken
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from infrastructure.persistence.models import RefreshTokenModel


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            is_revoked=model.is_revoked,
        )

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, token: RefreshToken) -> RefreshToken:
        model = RefreshTokenModel(
            id=token.id,
            user_id=token.user_id,
            token=token.token,
            expires_at=token.expires_at,
            is_revoked=token.is_revoked,
        )
        self._session.add(model)
        await self._session.flush()
        return token

    async def revoke(self, token: str) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token == token)
            .values(is_revoked=True)
        )

    async def revoke_all_for_user(self, user_id: str) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(is_revoked=True)
        )


__all__ = ["SQLAlchemyRefreshTokenRepository"]
