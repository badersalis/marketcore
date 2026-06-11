from application.dtos.auth_dtos import RegisterRequest, UserResponse
from domain.entities.user import User
from domain.exceptions.auth_exceptions import UserAlreadyExistsException
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.hashed_password import HashedPassword
from infrastructure.messaging.event_publisher import EventPublisher
from shared.events.user_events import UserRegistered


class RegisterUser:
    """Registers a new user account, persists it, and publishes a UserRegistered domain event."""

    def __init__(self, user_repo: UserRepository, event_publisher: EventPublisher) -> None:
        self._user_repo = user_repo
        self._event_publisher = event_publisher

    async def execute(self, request: RegisterRequest) -> UserResponse:
        existing = await self._user_repo.get_by_email(request.email)
        if existing:
            raise UserAlreadyExistsException(request.email)

        user = User(
            email=Email(request.email),
            hashed_password=HashedPassword.from_plain(request.password),
        )
        user = await self._user_repo.save(user)

        event = UserRegistered(user_id=user.id, email=str(user.email))
        await self._event_publisher.publish("user.events", event)

        return UserResponse(
            id=user.id,
            email=str(user.email),
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )


__all__ = ["RegisterUser"]
