"""
创建初始管理员账号
此脚本用于创建后台管理系统的第一个超级管理员账号。
"""
import sys
import asyncio
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.base import get_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.admin import Admin


async def create_first_admin():
    """创建第一个超级管理员账号"""

    # 管理员信息
    email = "admin@ai-interview.com"
    password = "ai-interview&admin"
    first_name = "AI-Interview"
    last_name = "Admin"

    engine = get_engine()
    async with AsyncSession(engine) as session:
        # 检查管理员是否已存在
        result = await session.execute(
            select(Admin).where(Admin.email == email)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f"❌ 邮箱为 {email} 的管理员已存在！")
            return

        # 创建新的超级管理员
        hashed_password = Admin.get_password_hash(password)
        admin = Admin(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            role="superadmin",
            is_active=True
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print("✅ 超级管理员账号创建成功！")
        print(f"   邮箱: {email}")
        print(f"   姓名: {first_name} {last_name}")
        print(f"   角色: superadmin")
        print(f"   ID: {admin.id}")


if __name__ == "__main__":
    asyncio.run(create_first_admin())
