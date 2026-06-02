from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta, UTC
from app.models.admin import Admin
from app.models.token import AdminToken
from app.core.security import AuthBase
from app.core.config import settings
from app.db.session import transaction
from app.exceptions.http_exceptions import APIException


class BackofficeAuthService(AuthBase):
    @staticmethod
    async def authenticate_admin(db: AsyncSession, email: str, password: str) -> Optional[Admin]:
        """管理员认证"""
        admin_query = select(Admin).where(Admin.email == email)
        result = await db.execute(admin_query)
        admin = result.scalar_one_or_none()

        if not admin or not admin.verify_password(password):
            return None
        return admin

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> Dict:
        """管理员登录"""
        async with transaction(db):
            admin = await BackofficeAuthService.authenticate_admin(db, email, password)
            if not admin:
                raise APIException(status_code=400, message="Incorrect email or password")
            if not admin.is_active:
                raise APIException(status_code=400, message="Admin account is inactive")

            # 标记旧token为无效
            stmt = update(AdminToken).where(
                (AdminToken.admin_id == admin.id) &
                (AdminToken.is_active == True)
            ).values(is_active=False)
            await db.execute(stmt)

            # 生成新的access token和refresh token
            access_token = AuthBase.create_access_token(
                str(admin.id),
                scope="backoffice",  # 区分客户端和后台
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            refresh_token = AuthBase.create_refresh_token(str(admin.id))

            # 存储新的refresh token
            hashed_token = AuthBase.hash_token(refresh_token)
            token = AdminToken(
                admin_id=admin.id,
                token=hashed_token,
                expires_at=datetime.now(UTC) + timedelta(days=7),
                is_active=True
            )
            db.add(token)
            await db.flush()

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }

    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> Dict:
        """刷新管理员token"""
        payload = AuthBase.verify_token(refresh_token, scope="refresh")
        if not payload:
            raise APIException(status_code=401, message="Invalid refresh token")

        admin_id = payload.get("sub")
        token_query = select(AdminToken).where(
            (AdminToken.admin_id == admin_id) &
            (AdminToken.is_active == True)
        )
        result = await db.execute(token_query)
        token = result.scalar_one_or_none()

        if not token or not AuthBase.verify_token_hash(refresh_token, token.token):
            raise APIException(status_code=401, message="Invalid or expired refresh token")

        token.last_used_at = datetime.now(UTC)
        await db.commit()

        access_token = AuthBase.create_access_token(
            admin_id,
            scope="backoffice",
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def logout(db: AsyncSession, refresh_token: str) -> None:
        """管理员登出"""
        payload = AuthBase.verify_token(refresh_token, scope="backoffice")
        if not payload:
            return  # 忽略无效token

        admin_id = payload.get("sub")
        token_query = select(AdminToken).where(
            (AdminToken.admin_id == admin_id) &
            (AdminToken.is_active == True)
        )
        result = await db.execute(token_query)
        token = result.scalar_one_or_none()

        if token:
            token.is_active = False
            await db.commit()


backoffice_auth_service = BackofficeAuthService()
