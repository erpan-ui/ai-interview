from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.client.deps import get_current_user
from app.schemas.client.auth import (
    UserRegister, RegisterResponse, Login, AuthToken, AccessToken,
    RefreshTokenRequest, LogoutRequest, SendVerificationCode, SendCodeResponse,
    VerifyEmail, SendPasswordResetCode, VerifyPasswordResetCode,
    PasswordResetToken, ResetPassword
)
from app.schemas.client.user import UserProfile
from app.services.client.auth import client_auth_service
from app.schemas.response import ApiResponse
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter()


@router.post("/register", response_model=AuthToken)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """用户注册（直接注册并登录）"""
    result = await client_auth_service.register_user(
        db, user_data.model_dump()
    )
    return ApiResponse.success(data=result)


@router.post("/send-verification-code", response_model=SendCodeResponse)
async def send_verification_code(
    request: SendVerificationCode,
    db: AsyncSession = Depends(get_db)
):
    """发送验证码"""
    result = await client_auth_service.send_verification_code(
        db, request.email, request.code_type
    )
    return ApiResponse.success(data=result)


@router.post("/verify-email", response_model=AuthToken)
async def verify_email(
    request: VerifyEmail,
    db: AsyncSession = Depends(get_db)
):
    """验证邮箱并自动登录"""
    result = await client_auth_service.verify_email_and_login(
        db, request.email, request.code
    )
    return ApiResponse.success(data=result)


@router.post("/login", response_model=AuthToken)
async def login(
    login_data: Login,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    result = await client_auth_service.login(
        db, login_data.email, login_data.password, login_data.remember_me
    )
    return ApiResponse.success(data=result)


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """刷新用户令牌"""
    result = await client_auth_service.refresh_token(db, request.refresh_token)
    return ApiResponse.success(data=result)


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登出"""
    await client_auth_service.logout(db, request.refresh_token)
    return ApiResponse.success_without_data()


@router.post("/password-reset/send-code")
async def send_password_reset_code(
    request: SendPasswordResetCode,
    db: AsyncSession = Depends(get_db)
):
    """发送密码重置验证码"""
    result = await client_auth_service.send_verification_code(
        db, request.email, "password-reset"
    )
    return ApiResponse.success(data=result)


@router.post("/password-reset/verify-code", response_model=PasswordResetToken)
async def verify_password_reset_code(
    request: VerifyPasswordResetCode,
    db: AsyncSession = Depends(get_db)
):
    """验证密码重置验证码"""
    reset_token = await client_auth_service.verify_password_reset_code(
        db, request.email, request.code
    )
    return ApiResponse.success(data={
        "reset_token": reset_token,
        "expires_in": 900  # 15 minutes
    })


@router.post("/password-reset/reset")
async def reset_password(
    request: ResetPassword,
    db: AsyncSession = Depends(get_db)
):
    """重置密码"""
    await client_auth_service.reset_password(
        db, request.reset_token, request.new_password
    )
    return ApiResponse.success_without_data(message="密码重置成功，请重新登录")


@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return ApiResponse.success(data={
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar": current_user.avatar,
        "phone": current_user.phone,
        "phone_country_code": current_user.phone_country_code,
        "university": current_user.university,
        "career_goal": current_user.career_goal,
        "contract_types": current_user.contract_types,
        "location": current_user.location,
        "gender": current_user.gender,
        "is_verified": current_user.is_verified,
        "email_verified_at": current_user.email_verified_at.isoformat() if current_user.email_verified_at else None,
        "last_active_at": current_user.last_active_at.isoformat() if current_user.last_active_at else None
    })


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    university: Optional[str] = None
    career_goal: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None


@router.put("/me")
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户资料"""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return ApiResponse.success(data={"message": "资料更新成功"})


AVATAR_DIR = "uploads/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传用户头像"""
    if not file.content_type or not file.content_type.startswith("image/"):
        return ApiResponse.error(message="仅支持图片文件")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        return ApiResponse.error(message="文件大小不能超过5MB")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    current_user.avatar = f"/uploads/avatars/{filename}"
    await db.commit()
    return ApiResponse.success(data={"avatar": current_user.avatar})


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


@router.post("/me/change-password")
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改用户密码"""
    if not current_user.verify_password(data.old_password):
        return ApiResponse.error(message="当前密码不正确")

    if len(data.new_password) < 6:
        return ApiResponse.error(message="新密码至少6位")

    current_user.hashed_password = User.get_password_hash(data.new_password)
    await db.commit()
    return ApiResponse.success(data={"message": "密码修改成功"})