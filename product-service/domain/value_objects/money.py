from dataclasses import dataclass
from decimal import Decimal

from shared.base_exception import DomainException


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise DomainException("Amount cannot be negative", "INVALID_AMOUNT")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise DomainException(
                f"Cannot add {self.currency} and {other.currency}", "CURRENCY_MISMATCH"
            )
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __mul__(self, factor: int) -> "Money":
        return Money(amount=self.amount * Decimal(str(factor)), currency=self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


__all__ = ["Money"]
