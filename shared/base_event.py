from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
import uuid


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = field(default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "occurred_at": self.occurred_at.isoformat(),
            "event_type": self.event_type,
        }


__all__ = ["DomainEvent"]
