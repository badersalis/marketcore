from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from domain.value_objects.kyc_status import KYCStatus


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None


class ProfileResponse(BaseModel):
    user_id: str
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    phone: Optional[str]
    updated_at: datetime

    model_config = {"from_attributes": True}


class KYCInquiryResponse(BaseModel):
    id: str
    user_id: str
    persona_inquiry_id: str
    redirect_url: str
    status: KYCStatus
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class KYCStatusResponse(BaseModel):
    has_inquiry: bool
    status: Optional[KYCStatus]
    inquiry_id: Optional[str]
    completed_at: Optional[datetime]


__all__ = [
    "UpdateProfileRequest",
    "ProfileResponse",
    "KYCInquiryResponse",
    "KYCStatusResponse",
]
