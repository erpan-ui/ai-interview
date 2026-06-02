from functools import wraps
from sqlalchemy.exc import IntegrityError
from app.exceptions.http_exceptions import ForeignKeyViolationError
import re


def handle_db_exceptions(func):
    """
    装饰器，用于处理数据库操作中的异常，特别是外键约束违反异常
    
    用法示例:
    @handle_db_exceptions
    async def delete_item(db: AsyncSession, item_id: int):
        # 删除操作代码
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            error_msg = str(e)
            # 检查是否是外键约束错误
            if "foreign key constraint fails" in error_msg.lower() or "FOREIGN KEY constraint failed" in error_msg:
                # 尝试从错误信息中提取相关表名
                referenced_table = extract_referenced_table(error_msg)
                if referenced_table:
                    raise ForeignKeyViolationError(
                        message=f"该记录已关联其他资源，请先将其标记为"停用"以对用户隐藏"
                    )
                else:
                    raise ForeignKeyViolationError()
            # 重新抛出原始异常
            raise
    return wrapper


def extract_referenced_table(error_message: str) -> str:
    """从错误信息中提取被引用的表名"""
    # MySQL 外键错误信息格式: "FOREIGN KEY constraint failed (table_name, CONSTRAINT ...)"
    # 或者 "foreign key constraint fails (`database`.`table`, CONSTRAINT ...)"
    try:
        # 尝试匹配 MySQL 错误格式
        match = re.search(r"constraint fails \(`[^`]*`.`([^`]*)`", error_message)
        if match:
            return match.group(1)
            
        # 尝试匹配 SQLite 错误格式
        match = re.search(r"FOREIGN KEY constraint failed \(([^,]*)", error_message)
        if match:
            return match.group(1)
            
        return ""
    except:
        return ""