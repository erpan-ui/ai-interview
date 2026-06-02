from typing import Optional, List, Literal
from pydantic import EmailStr, field_validator, Field
from ..base import BaseSchema
import re


class UserRegister(BaseSchema):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    phone_country_code: Optional[str] = None
    university: Optional[str] = None
    career_goal: Optional[Literal['find-a-job', 'improve-my-interview-skills', 'get-a-better-cv']] = Field(
        None,
        description="使用平台的主要目标。可选值：'find-a-job'（寻找工作机会）、'improve-my-interview-skills'（提升面试技巧）、'get-a-better-cv'（优化简历质量）",
        json_schema_extra={"enum": ["find-a-job", "improve-my-interview-skills", "get-a-better-cv"]}
    )
    contract_types: Optional[List[Literal['full-time', 'internship', 'apprenticeship']]] = Field(
        None,
        description="期望的合同类型。可选值：'full-time'（全职）、'internship'（实习）、'apprenticeship'（学徒）",
        json_schema_extra={"enum": ["full-time", "internship", "apprenticeship"]}
    )
    location: Optional[str] = None

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少8个字符')

        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含至少一个特殊字符')

        return v

    @field_validator('contract_types')
    def validate_contract_types(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v


class RegisterResponse(BaseSchema):
    user_id: int
    email: str
    message: str
    verification_required: bool = True


class Login(BaseSchema):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserProfile(BaseSchema):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_verified: bool
    university: Optional[str]
    career_goal: Optional[Literal['find-a-job', 'improve-my-interview-skills', 'get-a-better-cv']]
    location: Optional[str]


class AuthToken(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserProfile


class AccessToken(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class LogoutRequest(BaseSchema):
    refresh_token: str


class SendVerificationCode(BaseSchema):
    email: EmailStr
    code_type: Literal['registration', 'password-reset'] = Field(
        ...,
        description="验证码类型。可选值：'registration'（注册邮箱验证）、'password-reset'（密码重置验证）",
        json_schema_extra={"enum": ["registration", "password-reset"]}
    )


class SendCodeResponse(BaseSchema):
    message: str
    expires_in: int
    can_resend_at: int


class VerifyEmail(BaseSchema):
    email: EmailStr
    code: str

    @field_validator('code')
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('验证码必须为6位数字')
        return v


class SendPasswordResetCode(BaseSchema):
    email: EmailStr


class VerifyPasswordResetCode(BaseSchema):
    email: EmailStr
    code: str

    @field_validator('code')
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('验证码必须为6位数字')
        return v


class PasswordResetToken(BaseSchema):
    reset_token: str
    expires_in: int  # 秒


class ResetPassword(BaseSchema):
    reset_token: str
    new_password: str
    confirm_password: str

    @field_validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少8个字符')

        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含至少一个特殊字符')

        return v

    @field_validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('确认密码与新密码不一致')
        return v