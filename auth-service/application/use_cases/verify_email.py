from application.dtos.auth_dtos import UserResponse
from application.services.otp_service import OtpService
from domain.exceptions.auth_exceptions import (
    EmailAlreadyVerifiedException,
    InvalidOtpException,
    UserNotFoundException,
)
from domain.repositories.user_repository import UserRepository
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.user_events import UserVerified


class VerifyEmail:
    def __init__(
        self,
        user_repo: UserRepository,
        otp_service: OtpService,
        event_publisher: EventPublisher,
    ) -> None:
        self._user_repo = user_repo
        self._otp_service = otp_service
        self._event_publisher = event_publisher

    async def execute(self, email: str, otp: str) -> UserResponse:
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise InvalidOtpException()

        if user.is_verified:
            raise EmailAlreadyVerifiedException()

        valid = await self._otp_service.verify_and_consume(user.id, otp)
        if not valid:
            raise InvalidOtpException()

        user.verify()
        user = await self._user_repo.update(user)

        event = UserVerified(user_id=user.id, email=str(user.email))
        await self._event_publisher.publish("user.events", event)

        return UserResponse(
            id=user.id,
            email=str(user.email),
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )


__all__ = ["VerifyEmail"]
