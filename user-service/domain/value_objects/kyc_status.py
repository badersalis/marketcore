from enum import Enum


class KYCStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    EXPIRED = "expired"


__all__ = ["KYCStatus"]
