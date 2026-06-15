from enum import Enum


class PaymentStatus(str, Enum):
    """
    State machine: PENDING → PROCESSING → CONFIRMED
                   PENDING → PROCESSING → FAILED
                   PENDING → CANCELLED
    REFUNDED is a terminal state reachable only from CONFIRMED (future provider integration).
    """
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in (
            PaymentStatus.CONFIRMED,
            PaymentStatus.FAILED,
            PaymentStatus.REFUNDED,
            PaymentStatus.CANCELLED,
        )


__all__ = ["PaymentStatus"]
