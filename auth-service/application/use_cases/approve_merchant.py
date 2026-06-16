from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions.auth_exceptions import UserNotFoundException
from domain.repositories.user_repository import UserRepository
from domain.value_objects.role import UserRole
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.models import MerchantUpgradeRequestModel
from shared.events.user_events import MerchantApproved


class ApproveMerchant:
    """Operator approves a pending merchant upgrade request."""

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher,
        session: AsyncSession,
    ) -> None:
        self._user_repo = user_repo
        self._event_publisher = event_publisher
        self._session = session

    async def execute(self, request_id: str, reviewer_id: str) -> dict:
        result = await self._session.execute(
            select(MerchantUpgradeRequestModel).where(
                MerchantUpgradeRequestModel.id == request_id
            )
        )
        upgrade_request = result.scalar_one_or_none()
        if not upgrade_request:
            raise ValueError(f"Merchant upgrade request {request_id!r} not found")

        if upgrade_request.status != "pending":
            raise ValueError(f"Request is already {upgrade_request.status!r}")

        user = await self._user_repo.get_by_id(upgrade_request.user_id)
        if not user:
            raise UserNotFoundException()

        user.approve_merchant()
        await self._user_repo.update(user)

        upgrade_request.status = "approved"
        upgrade_request.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        upgrade_request.reviewer_id = reviewer_id
        await self._session.flush()

        event = MerchantApproved(user_id=user.id, email=str(user.email))
        await self._event_publisher.publish("user.events", event)

        return {"user_id": user.id, "role": user.role.value}


__all__ = ["ApproveMerchant"]
