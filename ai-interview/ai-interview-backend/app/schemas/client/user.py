from typing import Optional, List
from pydantic import EmailStr
from ..base import BaseSchema


class UserProfile(BaseSchema):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    phone_country_code: Optional[str]
    university: Optional[str]
    career_goal: Optional[str]
    contract_types: Optional[List[str]]
    location: Optional[str]
    is_verified: bool
    email_verified_at: Optional[str]  # ISO 格式时间字符串
    last_active_at: Optional[str]     # ISO 格式时间字符串


class UserUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    phone_country_code: Optional[str] = None
    university: Optional[str] = None
    career_goal: Optional[str] = None
    contract_types: Optional[List[str]] = None
    location: Optional[str] = None


class ChangePassword(BaseSchema):
    current_password: str
    new_password: str
    confirm_password: str