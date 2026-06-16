from domain.entities.user_profile import UserProfile
from domain.repositories.profile_repository import ProfileRepository
from application.dtos.user_dtos import ProfileResponse, UpdateProfileRequest


class UpdateProfile:
    def __init__(self, profile_repo: ProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def execute(self, user_id: str, request: UpdateProfileRequest) -> ProfileResponse:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, display_name=request.display_name or "")
            profile.update(
                avatar_url=request.avatar_url,
                bio=request.bio,
                phone=request.phone,
            )
        else:
            profile.update(
                display_name=request.display_name,
                avatar_url=request.avatar_url,
                bio=request.bio,
                phone=request.phone,
            )
        saved = await self._profile_repo.save(profile)
        return ProfileResponse(
            user_id=saved.user_id,
            display_name=saved.display_name,
            avatar_url=saved.avatar_url,
            bio=saved.bio,
            phone=saved.phone,
            updated_at=saved.updated_at,
        )
