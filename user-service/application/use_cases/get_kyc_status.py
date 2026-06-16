from domain.repositories.kyc_repository import KYCRepository
from application.dtos.user_dtos import KYCStatusResponse


class GetKYCStatus:
    def __init__(self, kyc_repo: KYCRepository) -> None:
        self._kyc_repo = kyc_repo

    async def execute(self, user_id: str) -> KYCStatusResponse:
        inquiry = await self._kyc_repo.get_latest_by_user_id(user_id)
        if inquiry is None:
            return KYCStatusResponse(
                has_inquiry=False,
                status=None,
                inquiry_id=None,
                completed_at=None,
            )
        return KYCStatusResponse(
            has_inquiry=True,
            status=inquiry.status,
            inquiry_id=inquiry.id,
            completed_at=inquiry.completed_at,
        )
