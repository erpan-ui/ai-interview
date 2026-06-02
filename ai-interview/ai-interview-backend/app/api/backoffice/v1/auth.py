from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.backoffice.deps import get_current_admin
from app.schemas.backoffice.auth import Token, Login, RefreshToken, Logout, AdminInfo
from app.services.backoffice.auth import backoffice_auth_service
from app.schemas.response import ApiResponse
from app.models.admin import Admin

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: Login,
    db: AsyncSession = Depends(get_db)
):
    """管理员登录"""
    result = await backoffice_auth_service.login(db, login_data.email, login_data.password)
    return ApiResponse.success(data=result)


@router.post("/refresh", response_model=Token)
async def refresh(
    request: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """刷新管理员token"""
    result = await backoffice_auth_service.refresh_token(db, request.refresh_token)
    return ApiResponse.success(data=result)


@router.post("/logout")
async def logout(
    request: Logout,
    db: AsyncSession = Depends(get_db),
):
    """管理员登出"""
    await backoffice_auth_service.logout(db, request.refresh_token)
    return ApiResponse.success_without_data()


@router.get("/me", response_model=AdminInfo)
async def get_current_admin_info(
    current_admin: Admin = Depends(get_current_admin)
):
    """获取当前管理员信息"""
    return ApiResponse.success(data=AdminInfo.model_validate(current_admin))
