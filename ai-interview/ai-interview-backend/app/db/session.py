from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from .base import get_session_local


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    AsyncSessionLocal = get_session_local()
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def transaction(db: AsyncSession):
    """事务上下文管理器，自动提交或回滚"""
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise


@asynccontextmanager
async def async_session():
    """为定时任务创建异步会话上下文管理器"""
    AsyncSessionLocal = get_session_local()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
