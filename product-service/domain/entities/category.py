from dataclasses import dataclass, field
from typing import Optional

from shared.base_entity import BaseEntity
from domain.value_objects.slug import Slug


@dataclass
class Category(BaseEntity):
    name: str = ""
    slug: Optional[Slug] = None

    def rename(self, name: str) -> None:
        self.name = name
        self.slug = Slug.from_string(name)


__all__ = ["Category"]
