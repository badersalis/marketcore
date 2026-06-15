from dataclasses import dataclass


@dataclass(frozen=True)
class IdempotencyKey:
    """
    Caller-supplied key used to make payment intent creation safe to retry.
    The repository MUST enforce uniqueness on this key.
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value or not (1 <= len(self.value) <= 255):
            raise ValueError("Idempotency key must be 1–255 characters")

    def __str__(self) -> str:
        return self.value


__all__ = ["IdempotencyKey"]
