from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

from domain.value_objects.kyc_status import KYCStatus


@dataclass
class KYCInquiry:
    user_id: str
    persona_inquiry_id: str
    redirect_url: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: KYCStatus = KYCStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def mark_completed(self) -> None:
        self.status = KYCStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        self.status = KYCStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)

    def mark_needs_review(self) -> None:
        self.status = KYCStatus.NEEDS_REVIEW

    def mark_expired(self) -> None:
        self.status = KYCStatus.EXPIRED
        self.completed_at = datetime.now(timezone.utc)


__all__ = ["KYCInquiry"]
