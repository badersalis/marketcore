from domain.entities.kyc_inquiry import KYCInquiry
from domain.exceptions.user_exceptions import KYCAlreadySubmittedException
from domain.repositories.kyc_repository import KYCRepository
from domain.value_objects.kyc_status import KYCStatus
from infrastructure.clients.persona_client import PersonaClient
from infrastructure.messaging.event_publisher import EventPublisher
from application.dtos.user_dtos import KYCInquiryResponse
from shared.events.user_events import KYCInquiryCreated


class CreateKYCInquiry:
    def __init__(
        self,
        kyc_repo: KYCRepository,
        persona_client: PersonaClient,
        event_publisher: EventPublisher,
    ) -> None:
        self._kyc_repo = kyc_repo
        self._persona_client = persona_client
        self._publisher = event_publisher

    async def execute(self, user_id: str) -> KYCInquiryResponse:
        pending = await self._kyc_repo.get_pending_by_user_id(user_id)
        if pending is not None:
            raise KYCAlreadySubmittedException()

        persona_data = await self._persona_client.create_inquiry(reference_id=user_id)

        inquiry = KYCInquiry(
            user_id=user_id,
            persona_inquiry_id=persona_data["inquiry_id"],
            redirect_url=persona_data["redirect_url"],
        )
        saved = await self._kyc_repo.save(inquiry)

        await self._publisher.publish(
            KYCInquiryCreated(
                user_id=user_id,
                inquiry_id=saved.id,
                persona_inquiry_id=saved.persona_inquiry_id,
            )
        )

        return KYCInquiryResponse(
            id=saved.id,
            user_id=saved.user_id,
            persona_inquiry_id=saved.persona_inquiry_id,
            redirect_url=saved.redirect_url,
            status=saved.status,
            created_at=saved.created_at,
            completed_at=saved.completed_at,
        )
