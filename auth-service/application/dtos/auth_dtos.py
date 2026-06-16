from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from domain.value_objects.role import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    is_verified: bool
    role: UserRole
    is_merchant_approved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SendVerificationRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class AssignRoleRequest(BaseModel):
    user_id: str
    role: UserRole


__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "UserResponse",
    "SendVerificationRequest",
    "VerifyOtpRequest",
    "AssignRoleRequest",
]
