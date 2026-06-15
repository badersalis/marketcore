import logging

from application.services.otp_service import OtpService
from core.config import settings
from domain.exceptions.auth_exceptions import EmailAlreadyVerifiedException
from domain.repositories.user_repository import UserRepository
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.user_events import VerificationEmailRequested

logger = logging.getLogger(__name__)


class SendVerificationEmail:
    """
    Generates a fresh OTP and publishes VerificationEmailRequested.
    Intentionally silent when the email is not found — never confirm whether an address exists.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        otp_service: OtpService,
        event_publisher: EventPublisher,
    ) -> None:
        self._user_repo = user_repo
        self._otp_service = otp_service
        self._event_publisher = event_publisher

    async def execute(self, email: str) -> None:
        user = await self._user_repo.get_by_email(email)
        if not user:
            logger.info("OTP requested for unknown email — silently ignored")
            return

        if user.is_verified:
            raise EmailAlreadyVerifiedException()

        otp = self._otp_service.generate()
        await self._otp_service.store(user.id, otp, settings.OTP_EXPIRE_MINUTES)

        event = VerificationEmailRequested(
            user_id=user.id,
            email=email,
            otp=otp,
        )
        await self._event_publisher.publish("user.events", event)


__all__ = ["SendVerificationEmail"]
