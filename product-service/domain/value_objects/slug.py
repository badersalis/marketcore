import re
from dataclasses import dataclass

from shared.base_exception import DomainException


@dataclass(frozen=True)
class Slug:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise DomainException("Slug cannot be empty", "INVALID_SLUG")

    @classmethod
    def from_string(cls, s: str) -> "Slug":
        slug = re.sub(r"[^a-zA-Z0-9\s\-]", "", s.lower()).strip()
        slug = re.sub(r"[\s\-]+", "-", slug)
        if not slug:
            raise DomainException(f"Cannot generate slug from: {s!r}", "INVALID_SLUG")
        return cls(value=slug)

    def __str__(self) -> str:
        return self.value


__all__ = ["Slug"]
