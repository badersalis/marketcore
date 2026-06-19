import logging

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

_RESEND_API = "https://api.resend.com/emails"


class ResendEmailSender:
    """Sends transactional email via the Resend REST API.

    If RESEND_API_KEY is not configured the send is skipped and a warning
    is logged, so local development works without a real account.
    """

    async def send(self, *, to: str, subject: str, html: str) -> None:
        if not settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY not set — skipping email to %s | subject: %s", to, subject)
            return

        payload = {
            "from": settings.EMAIL_FROM,
            "to": [to],
            "subject": subject,
            "html": html,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(
                    _RESEND_API,
                    headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                    json=payload,
                )
                response.raise_for_status()
                logger.info(
                    "Email sent to %s | subject: %s | id: %s",
                    to, subject, response.json().get("id"),
                )
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Resend API error %s for %s: %s",
                    exc.response.status_code, to, exc.response.text,
                )
                raise
            except httpx.RequestError as exc:
                logger.error("Resend request failed for %s: %s", to, exc)
                raise


__all__ = ["ResendEmailSender"]
