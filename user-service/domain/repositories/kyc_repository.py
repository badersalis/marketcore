from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.kyc_inquiry import KYCInquiry


class KYCRepository(ABC):
    @abstractmethod
    async def get_by_id(self, inquiry_id: str) -> Optional[KYCInquiry]: ...

    @abstractmethod
    async def get_by_persona_inquiry_id(self, persona_inquiry_id: str) -> Optional[KYCInquiry]: ...

    @abstractmethod
    async def get_latest_by_user_id(self, user_id: str) -> Optional[KYCInquiry]: ...

    @abstractmethod
    async def get_pending_by_user_id(self, user_id: str) -> Optional[KYCInquiry]: ...

    @abstractmethod
    async def save(self, inquiry: KYCInquiry) -> KYCInquiry: ...

    @abstractmethod
    async def update(self, inquiry: KYCInquiry) -> KYCInquiry: ...


__all__ = ["KYCRepository"]
