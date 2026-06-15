from application.dtos.payment_dtos import PaymentListResponse, PaymentResponse
from domain.exceptions.payment_exceptions import (
    PaymentNotFoundException,
    UnauthorizedPaymentAccessException,
)
from domain.repositories.payment_repository import PaymentRepository


class GetPaymentStatus:
    def __init__(self, payment_repo: PaymentRepository) -> None:
        self._payment_repo = payment_repo

    async def execute(self, payment_id: str, requesting_user_id: str) -> PaymentResponse:
        payment = await self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundException(payment_id)

        if payment.user_id != requesting_user_id:
            raise UnauthorizedPaymentAccessException()

        return PaymentResponse(
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


class ListUserPayments:
    def __init__(self, payment_repo: PaymentRepository) -> None:
        self._payment_repo = payment_repo

    async def execute(
        self, user_id: str, offset: int = 0, limit: int = 20
    ) -> PaymentListResponse:
        payments = await self._payment_repo.list_by_user_id(
            user_id=user_id, offset=offset, limit=limit
        )
        items = [
            PaymentResponse(
                id=p.id,
                order_id=p.order_id,
                user_id=p.user_id,
                amount=p.amount_value,
                currency=p.currency,
                status=p.status.value,
                idempotency_key=p.idempotency_key,
                provider_reference=p.provider_reference,
                failure_reason=p.failure_reason,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in payments
        ]
        return PaymentListResponse(
            items=items,
            total=len(items),
            offset=offset,
            limit=limit,
        )


__all__ = ["GetPaymentStatus", "ListUserPayments"]
