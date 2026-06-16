from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import settings

_security = HTTPBearer(auto_error=False)


async def get_current_user_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security),
) -> dict:
    if not credentials:
        # Support pre-validated header from api-gateway
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*roles: str):
    async def dependency(payload: dict = Depends(get_current_user_payload)) -> dict:
        if payload.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {list(roles)}",
            )
        return payload
    return dependency


require_member = require_role("member", "merchant", "operator")
require_operator = require_role("operator")

__all__ = ["get_current_user_payload", "require_role", "require_member", "require_operator"]
