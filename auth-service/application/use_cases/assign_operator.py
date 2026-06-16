from domain.exceptions.auth_exceptions import UserNotFoundException
from domain.repositories.user_repository import UserRepository
from domain.value_objects.role import UserRole


class AssignOperator:
    """Operator assigns the operator role to another user."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, target_user_id: str) -> dict:
        user = await self._user_repo.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundException()

        user.assign_role(UserRole.OPERATOR)
        await self._user_repo.update(user)

        return {"user_id": user.id, "role": user.role.value}


__all__ = ["AssignOperator"]
