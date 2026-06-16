import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from core.config import settings
from domain.value_objects.role import UserRole


class TokenService:
    def create_access_token(self, user_id: str, email: str = "", role: UserRole = UserRole.MEMBER) -> str:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role.value,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token_value(self) -> str:
        return secrets.token_urlsafe(64)

    def decode_access_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    def decode_token_payload(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None


__all__ = ["TokenService"]
