import logging
from typing import Any, Dict

from domain.repositories.kyc_repository import KYCRepository
from domain.value_objects.kyc_status import KYCStatus
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.user_events import KYCStatusUpdated

logger = logging.getLogger(__name__)

_PERSONA_TO_STATUS: Dict[str, KYCStatus] = {
    "completed": KYCStatus.COMPLETED,
    "failed": KYCStatus.FAILED,
    "declined": KYCStatus.FAILED,
    "needs_review": KYCStatus.NEEDS_REVIEW,
    "expired": KYCStatus.EXPIRED,
}


class ProcessKYCWebhook:
    def __init__(
        self,
        kyc_repo: KYCRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._kyc_repo = kyc_repo
        self._publisher = event_publisher

    async def execute(self, payload: Dict[str, Any]) -> None:
        event_name: str = payload.get("data", {}).get("attributes", {}).get("name", "")
        inquiry_id: str = (
            payload.get("data", {})
            .get("relationships", {})
            .get("inquiry", {})
            .get("data", {})
            .get("id", "")
        )

        if not inquiry_id:
            logger.warning("Persona webhook missing inquiry id, skipping")
            return

        new_status = _PERSONA_TO_STATUS.get(event_name.replace("inquiry.", ""))
        if new_status is None:
            logger.info("Unhandled Persona event %s, skipping", event_name)
            return

        inquiry = await self._kyc_repo.get_by_persona_inquiry_id(inquiry_id)
        if inquiry is None:
            logger.warning("Received webhook for unknown inquiry %s", inquiry_id)
            return

        if new_status == KYCStatus.COMPLETED:
            inquiry.mark_completed()
        elif new_status == KYCStatus.FAILED:
            inquiry.mark_failed()
        elif new_status == KYCStatus.NEEDS_REVIEW:
            inquiry.mark_needs_review()
        elif new_status == KYCStatus.EXPIRED:
            inquiry.mark_expired()

        await self._kyc_repo.update(inquiry)

        await self._publisher.publish(
            KYCStatusUpdated(
                user_id=inquiry.user_id,
                inquiry_id=inquiry.id,
                new_status=new_status.value,
            )
        )

        logger.info(
            "KYC inquiry %s for user %s → %s",
            inquiry.id,
            inquiry.user_id,
            new_status.value,
        )
