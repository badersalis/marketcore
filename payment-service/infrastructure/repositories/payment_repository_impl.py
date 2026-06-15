from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.payment import Payment
from domain.repositories.payment_repository import PaymentRepository
from domain.value_objects.money import Money
from domain.value_objects.payment_status import PaymentStatus
from infrastructure.persistence.models import PaymentModel


class SQLAlchemyPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            order_id=model.order_id,
            user_id=model.user_id,
            amount=Money(amount=Decimal(str(model.amount)), currency=model.currency),
            status=PaymentStatus(model.status),
            idempotency_key=model.idempotency_key,
            provider_reference=model.provider_reference,
            failure_reason=model.failure_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_idempotency_key(self, key: str) -> Optional[Payment]:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.idempotency_key == key)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.order_id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user_id(
        self, user_id: str, offset: int = 0, limit: int = 20
    ) -> list[Payment]:
        result = await self._session.execute(
            select(PaymentModel)
            .where(PaymentModel.user_id == user_id)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, payment: Payment) -> Payment:
        model = PaymentModel(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=payment.amount_value,
            currency=payment.currency,
            status=payment.status.value,
            idempotency_key=payment.idempotency_key,
            provider_reference=payment.provider_reference,
            failure_reason=payment.failure_reason,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return payment

    async def update(self, payment: Payment) -> Payment:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment.id)
        )
        model = result.scalar_one()
        model.status = payment.status.value
        model.provider_reference = payment.provider_reference
        model.failure_reason = payment.failure_reason
        model.updated_at = payment.updated_at
        await self._session.flush()
        return payment


__all__ = ["SQLAlchemyPaymentRepository"]
