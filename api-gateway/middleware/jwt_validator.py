import logging
from typing import Optional

from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.config import PUBLIC_ROUTES, is_public_product_route, settings

logger = logging.getLogger(__name__)


class JWTValidationMiddleware(BaseHTTPMiddleware):
    """Validates Bearer tokens on protected routes and injects user claims as headers."""

    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path

        if self._is_public(method, path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Not authenticated"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        payload = self._decode(token)
        if not payload:
            return JSONResponse(
                {"detail": "Invalid or expired token"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Inject claims so upstream services can trust them without re-validating
        headers = dict(request.headers)
        headers["X-User-Id"] = payload.get("sub", "")
        headers["X-User-Role"] = payload.get("role", "member")
        headers["X-User-Email"] = payload.get("email", "")

        request.state.user_id = payload.get("sub", "")
        request.state.user_role = payload.get("role", "member")

        scope = dict(request.scope)
        scope["headers"] = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
        request._headers = None  # reset cached headers
        request = Request(scope, request.receive, request.send)

        return await call_next(request)

    def _is_public(self, method: str, path: str) -> bool:
        if (method, path) in PUBLIC_ROUTES:
            return True
        if is_public_product_route(method, path):
            return True
        return False

    def _decode(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None


__all__ = ["JWTValidationMiddleware"]
