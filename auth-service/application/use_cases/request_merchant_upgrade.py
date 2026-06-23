from domain.exceptions.auth_exceptions import UserNotFoundException
from domain.repositories.user_repository import UserRepository
from domain.value_objects.role import UserRole
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.models import MerchantUpgradeRequestModel
from shared.base_entity import BaseEntity
from shared.events.user_events import MerchantUpgradeRequested
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class RequestMerchantUpgrade:
    """A member requests promotion to merchant role. Creates a pending request and notifies operators."""

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher,
        session: AsyncSession,
    ) -> None:
        self._user_repo = user_repo
        self._event_publisher = event_publisher
        self._session = session

    async def execute(self, user_id: str) -> dict:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        request_id = BaseEntity().id
        record = MerchantUpgradeRequestModel(
            id=request_id,
            user_id=user_id,
            status="pending",
        )
        self._session.add(record)
        await self._session.flush()

        event = MerchantUpgradeRequested(
            user_id=user.id,
            email=str(user.email),
            request_id=request_id,
        )
        await self._event_publisher.publish("user.events", event)

        return {"request_id": request_id, "status": "pending"}


__all__ = ["RequestMerchantUpgrade"]
