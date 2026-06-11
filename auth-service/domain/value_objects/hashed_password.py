from dataclasses import dataclass

import bcrypt


@dataclass(frozen=True)
class HashedPassword:
    value: str

    @classmethod
    def from_plain(cls, plain: str) -> "HashedPassword":
        hashed = bcrypt.hashpw(plain.encode()[:72], bcrypt.gensalt())
        return cls(value=hashed.decode())

    def verify(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode()[:72], self.value.encode())


__all__ = ["HashedPassword"]
