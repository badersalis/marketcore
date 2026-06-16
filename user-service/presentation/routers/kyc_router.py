import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.user_dtos import KYCInquiryResponse, KYCStatusResponse
from application.use_cases.create_kyc_inquiry import CreateKYCInquiry
from application.use_cases.get_kyc_status import GetKYCStatus
from application.use_cases.process_kyc_webhook import ProcessKYCWebhook
from domain.exceptions.user_exceptions import KYCAlreadySubmittedException
from infrastructure.clients.persona_client import PersonaClient, PersonaVerificationError
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import get_db
from infrastructure.repositories.kyc_repository_impl import SQLAlchemyKYCRepository
from presentation.dependencies.permissions import require_member

logger = logging.getLogger(__name__)
router = APIRouter()


def _publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


def _persona(request: Request) -> PersonaClient:
    return request.app.state.persona_client


@router.post("/inquiries", response_model=KYCInquiryResponse, status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    payload: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(_publisher),
    persona: PersonaClient = Depends(_persona),
) -> KYCInquiryResponse:
    use_case = CreateKYCInquiry(
        kyc_repo=SQLAlchemyKYCRepository(db),
        persona_client=persona,
        event_publisher=publisher,
    )
    try:
        return await use_case.execute(user_id=payload["sub"])
    except KYCAlreadySubmittedException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except PersonaVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.get("/status", response_model=KYCStatusResponse)
async def get_status(
    payload: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
) -> KYCStatusResponse:
    use_case = GetKYCStatus(SQLAlchemyKYCRepository(db))
    return await use_case.execute(user_id=payload["sub"])


@router.post("/webhook", status_code=status.HTTP_200_OK, include_in_schema=False)
async def persona_webhook(
    request: Request,
    publisher: EventPublisher = Depends(_publisher),
    persona: PersonaClient = Depends(_persona),
) -> dict:
    """Persona posts verification results here. We verify the signature and enqueue."""
    raw_body = await request.body()
    sig_header = request.headers.get("Persona-Signature", "")

    if not persona.verify_webhook_signature(raw_body, sig_header):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    await publisher.publish_raw("kyc.webhooks", raw_body)
    return {"received": True}


__all__ = ["router"]
