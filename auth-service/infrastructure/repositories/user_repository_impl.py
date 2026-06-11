from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.hashed_password import HashedPassword
from infrastructure.persistence.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            hashed_password=HashedPassword(model.hashed_password),
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
        )

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=str(user.email),
            hashed_password=user.hashed_password.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return user

    async def update(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one()
        model.email = str(user.email)
        model.hashed_password = user.hashed_password.value
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        await self._session.flush()
        return user


__all__ = ["SQLAlchemyUserRepository"]
