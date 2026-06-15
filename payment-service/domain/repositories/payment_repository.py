from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> Optional[Payment]:
        """Used by CreatePaymentIntent to detect duplicate submissions."""
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    async def list_by_user_id(
        self, user_id: str, offset: int = 0, limit: int = 20
    ) -> list[Payment]:
        pass

    @abstractmethod
    async def save(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        pass


__all__ = ["PaymentRepository"]
