"""
初始化默认管理员账号
运行方式: docker exec -it prepwise-app python -m app.scripts.seed_admin
"""
import asyncio
from sqlalchemy import select
from app.db.session import async_session
from app.models.admin import Admin


async def seed():
    async with async_session() as db:
        # 检查管理员是否已存在
        result = await db.execute(select(Admin).where(Admin.email == "admin@prepwise.com"))
        if result.scalar_one_or_none():
            print("管理员已存在，跳过创建。")
            return

        admin = Admin(
            email="admin@prepwise.com",
            first_name="Admin",
            last_name="Prepwise",
            password=Admin.get_password_hash("admin123"),
            role="superadmin",
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("默认管理员已创建: admin@prepwise.com / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
