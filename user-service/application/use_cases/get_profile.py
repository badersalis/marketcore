from domain.entities.user_profile import UserProfile
from domain.repositories.profile_repository import ProfileRepository
from application.dtos.user_dtos import ProfileResponse


class GetProfile:
    def __init__(self, profile_repo: ProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def execute(self, user_id: str) -> ProfileResponse:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, display_name="")
            profile = await self._profile_repo.save(profile)
        return ProfileResponse(
            user_id=profile.user_id,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            phone=profile.phone,
            updated_at=profile.updated_at,
        )
