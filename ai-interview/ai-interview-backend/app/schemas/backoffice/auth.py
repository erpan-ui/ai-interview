from ..base import BaseSchema, BaseResponseSchema
from pydantic import EmailStr
from datetime import datetime
from typing import Optional


class Login(BaseSchema):
    email: EmailStr
    password: str


class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseSchema):
    refresh_token: str


class Logout(BaseSchema):
    refresh_token: str


class AdminInfo(BaseResponseSchema):
    id: int
    role: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
