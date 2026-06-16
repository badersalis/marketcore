from datetime import timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.kyc_inquiry import KYCInquiry
from domain.repositories.kyc_repository import KYCRepository
from domain.value_objects.kyc_status import KYCStatus
from infrastructure.persistence.models import KYCInquiryModel


class SQLAlchemyKYCRepository(KYCRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, inquiry_id: str) -> Optional[KYCInquiry]:
        result = await self._session.execute(
            select(KYCInquiryModel).where(KYCInquiryModel.id == inquiry_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_persona_inquiry_id(self, persona_inquiry_id: str) -> Optional[KYCInquiry]:
        result = await self._session.execute(
            select(KYCInquiryModel).where(
                KYCInquiryModel.persona_inquiry_id == persona_inquiry_id
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_latest_by_user_id(self, user_id: str) -> Optional[KYCInquiry]:
        result = await self._session.execute(
            select(KYCInquiryModel)
            .where(KYCInquiryModel.user_id == user_id)
            .order_by(KYCInquiryModel.created_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_pending_by_user_id(self, user_id: str) -> Optional[KYCInquiry]:
        result = await self._session.execute(
            select(KYCInquiryModel).where(
                KYCInquiryModel.user_id == user_id,
                KYCInquiryModel.status == KYCStatus.PENDING,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, inquiry: KYCInquiry) -> KYCInquiry:
        model = KYCInquiryModel(
            id=inquiry.id,
            user_id=inquiry.user_id,
            persona_inquiry_id=inquiry.persona_inquiry_id,
            redirect_url=inquiry.redirect_url,
            status=inquiry.status,
            created_at=inquiry.created_at,
            completed_at=inquiry.completed_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, inquiry: KYCInquiry) -> KYCInquiry:
        result = await self._session.execute(
            select(KYCInquiryModel).where(KYCInquiryModel.id == inquiry.id)
        )
        model = result.scalar_one()
        model.status = inquiry.status
        model.completed_at = inquiry.completed_at
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: KYCInquiryModel) -> KYCInquiry:
        created_at = model.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        completed_at = model.completed_at
        if completed_at is not None and completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)
        return KYCInquiry(
            id=model.id,
            user_id=model.user_id,
            persona_inquiry_id=model.persona_inquiry_id,
            redirect_url=model.redirect_url,
            status=KYCStatus(model.status),
            created_at=created_at,
            completed_at=completed_at,
        )
