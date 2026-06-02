from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class WaitingListSubmitRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    email: EmailStr = Field(..., description="User's email address")
    university: Optional[str] = Field(None, max_length=255, description="User's university")

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

    @field_validator('university')
    @classmethod
    def validate_university(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip()
        return v


class WaitingListSubmitResponse(BaseModel):
    email: str
    message: str


class WaitingListResendRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")


class WaitingListVerifyResponse(BaseModel):
    message: str
    email: str
    verified_at: datetime