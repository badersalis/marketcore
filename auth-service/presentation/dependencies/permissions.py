from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.services.token_service import TokenService
from domain.value_objects.role import UserRole

_security = HTTPBearer()
_token_service = TokenService()


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> dict:
    payload = _token_service.decode_token_payload(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def require_role(*roles: UserRole):
    """Return a FastAPI dependency that enforces one of the given roles."""

    async def dependency(
        payload: dict = Depends(get_current_user_payload),
    ) -> dict:
        user_role = payload.get("role", UserRole.MEMBER.value)
        if user_role not in {r.value for r in roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {[r.value for r in roles]}",
            )
        return payload

    return dependency


require_member = require_role(UserRole.MEMBER, UserRole.MERCHANT, UserRole.OPERATOR)
require_merchant = require_role(UserRole.MERCHANT, UserRole.OPERATOR)
require_operator = require_role(UserRole.OPERATOR)

__all__ = [
    "get_current_user_payload",
    "require_role",
    "require_member",
    "require_merchant",
    "require_operator",
]
