import re
from dataclasses import dataclass

from shared.base_exception import DomainException

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise DomainException(f"Invalid email address: {self.value}", "INVALID_EMAIL")

    def __str__(self) -> str:
        return self.value


__all__ = ["Email"]
