from enum import Enum


class UserRole(str, Enum):
    MEMBER = "member"
    MERCHANT = "merchant"
    OPERATOR = "operator"


__all__ = ["UserRole"]
