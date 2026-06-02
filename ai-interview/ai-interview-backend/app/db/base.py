from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from .models import Base

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# 延迟创建引擎，避免 Alembic 迁移时的导入问题
engine = None
AsyncSessionLocal = None

def get_engine():
    """获取或创建异步数据库引擎"""
    global engine
    if engine is None:
        engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL,
            echo=True,
            future=True,
            pool_pre_ping=True,
            # 增强连接池配置以提高稳定性
            pool_recycle=1800,  # 30分钟内回收连接
            pool_timeout=30,    # 获取连接的超时时间
            max_overflow=10,    # 允许的最大连接溢出数
            pool_size=20,       # 连接池大小
        )
    return engine

def get_session_local():
    """获取或创建异步会话工厂"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(bind=get_engine(), class_=AsyncSession, expire_on_commit=False)
    return AsyncSessionLocal

# 为调度任务创建一个独立的引擎和会话工厂
# 这样每个调度任务都会使用自己的连接池和事件循环
def create_scheduler_engine():
    """为调度任务创建独立的数据库引擎，确保不会与主应用程序共享事件循环"""
    return create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True,
        future=True,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_timeout=30,
        max_overflow=5,
        pool_size=5,
    )

def create_scheduler_session_factory(engine):
    """为调度任务创建独立的会话工厂"""
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def close_db_engine():
    """关闭数据库引擎和连接池"""
    if engine is not None:
        await engine.dispose()
