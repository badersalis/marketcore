from datetime import timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user_profile import UserProfile
from domain.repositories.profile_repository import ProfileRepository
from infrastructure.persistence.models import UserProfileModel


class SQLAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        result = await self._session.execute(
            select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, profile: UserProfile) -> UserProfile:
        result = await self._session.execute(
            select(UserProfileModel).where(UserProfileModel.user_id == profile.user_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            model = UserProfileModel(
                user_id=profile.user_id,
                display_name=profile.display_name,
                avatar_url=profile.avatar_url,
                bio=profile.bio,
                phone=profile.phone,
                updated_at=profile.updated_at,
            )
            self._session.add(model)
        else:
            model.display_name = profile.display_name
            model.avatar_url = profile.avatar_url
            model.bio = profile.bio
            model.phone = profile.phone
            model.updated_at = profile.updated_at

        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UserProfileModel) -> UserProfile:
        updated_at = model.updated_at
        if updated_at.tzinfo is None:
            from datetime import timezone
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        return UserProfile(
            user_id=model.user_id,
            display_name=model.display_name,
            avatar_url=model.avatar_url,
            bio=model.bio,
            phone=model.phone,
            updated_at=updated_at,
        )
