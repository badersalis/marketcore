from shared.base_exception import DomainException
from domain.value_objects.payment_status import PaymentStatus


class PaymentNotFoundException(DomainException):
    def __init__(self, payment_id: str):
        super().__init__(f"Payment '{payment_id}' not found", "PAYMENT_NOT_FOUND")


class DuplicateIdempotencyKeyException(DomainException):
    """Raised when a key collision is detected but the existing payment differs in amount/user."""
    def __init__(self, key: str):
        super().__init__(
            f"Idempotency key '{key}' already used with different parameters",
            "IDEMPOTENCY_CONFLICT",
        )


class InvalidPaymentTransitionException(DomainException):
    def __init__(self, current: PaymentStatus, target: PaymentStatus):
        super().__init__(
            f"Cannot transition payment from '{current}' to '{target}'",
            "INVALID_PAYMENT_TRANSITION",
        )


class PaymentAlreadyTerminalException(DomainException):
    def __init__(self, payment_id: str, status: PaymentStatus):
        super().__init__(
            f"Payment '{payment_id}' is already in terminal state '{status}'",
            "PAYMENT_ALREADY_TERMINAL",
        )


class UnauthorizedPaymentAccessException(DomainException):
    def __init__(self) -> None:
        super().__init__("You do not have access to this payment", "UNAUTHORIZED_PAYMENT_ACCESS")


__all__ = [
    "PaymentNotFoundException",
    "DuplicateIdempotencyKeyException",
    "InvalidPaymentTransitionException",
    "PaymentAlreadyTerminalException",
    "UnauthorizedPaymentAccessException",
]
