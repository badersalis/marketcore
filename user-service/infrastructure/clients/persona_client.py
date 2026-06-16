import hashlib
import hmac
import logging
import time
from typing import Any, Dict

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

_PERSONA_BASE_URL = "https://withpersona.com/api/v1"
_PERSONA_API_VERSION = "2023-01-05"


class PersonaVerificationError(Exception):
    pass


class PersonaClient:
    def __init__(self) -> None:
        self._api_key = settings.PERSONA_API_KEY
        self._inquiry_type_id = settings.PERSONA_INQUIRY_TYPE_ID
        self._webhook_secret = settings.PERSONA_WEBHOOK_SECRET

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Persona-Version": _PERSONA_API_VERSION,
            "Content-Type": "application/json",
        }

    async def create_inquiry(self, reference_id: str) -> Dict[str, Any]:
        payload = {
            "data": {
                "attributes": {
                    "inquiry-type-id": self._inquiry_type_id,
                    "reference-id": reference_id,
                }
            }
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{_PERSONA_BASE_URL}/inquiries",
                json=payload,
                headers=self._headers(),
            )
        if response.status_code not in (200, 201):
            logger.error("Persona inquiry creation failed: %s", response.text)
            raise PersonaVerificationError(
                f"Persona API returned {response.status_code}"
            )

        data = response.json()["data"]
        attrs = data["attributes"]
        return {
            "inquiry_id": data["id"],
            "redirect_url": attrs.get("redirect-url", ""),
            "resume_url": attrs.get("resume-url", ""),
            "status": attrs.get("status", "created"),
        }

    def verify_webhook_signature(self, raw_body: bytes, signature_header: str) -> bool:
        """Verify Persona webhook signature (t=<ts>,v1=<sig> format)."""
        try:
            parts = dict(item.split("=", 1) for item in signature_header.split(","))
            timestamp = parts["t"]
            expected_sig = parts["v1"]
        except (KeyError, ValueError):
            return False

        # Reject replays older than 5 minutes
        if abs(time.time() - int(timestamp)) > 300:
            return False

        signed_payload = f"{timestamp}.{raw_body.decode()}"
        computed = hmac.new(
            self._webhook_secret.encode(),
            signed_payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed, expected_sig)


__all__ = ["PersonaClient", "PersonaVerificationError"]
