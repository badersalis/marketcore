from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if self.amount < Decimal("0"):
            raise ValueError("Money amount cannot be negative")
        if len(self.currency) != 3 or not self.currency.isalpha():
            raise ValueError(f"Invalid ISO-4217 currency code: '{self.currency}'")
        # Normalize to 2 decimal places
        object.__setattr__(
            self, "amount", self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add {self.currency} and {other.currency} — convert first"
            )
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __repr__(self) -> str:
        return f"{self.amount} {self.currency}"


__all__ = ["Money"]
