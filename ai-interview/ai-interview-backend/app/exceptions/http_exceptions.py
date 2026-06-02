from fastapi import HTTPException
from typing import Any, Optional
from app.common.language import get_message


class APIException(HTTPException):
    def __init__(
        self,
        code: int = 10000,
        message: str = "API 异常",
        status_code: int = 400,
        data: Any = None,
        language: Optional[str] = None
    ) -> None:
        # 根据语言翻译消息
        translated_message = get_message(message, language)
        super().__init__(status_code=status_code, detail=translated_message)
        self.code = code  # 业务错误码
        self.data = data  # 可选的额外数据


# 常见异常类型
class ValidationError(APIException):
    """参数验证错误"""
    def __init__(self, message: str = "参数验证错误", data: Any = None, language: Optional[str] = None):
        super().__init__(code=1001, message=message, status_code=400, data=data, language=language)


class AuthenticationError(APIException):
    """认证失败"""
    def __init__(self, message: str = "认证失败", data: Any = None, language: Optional[str] = None):
        super().__init__(code=1002, message=message, status_code=401, data=data, language=language)


class AuthorizationError(APIException):
    """权限不足"""
    def __init__(self, message: str = "权限不足", data: Any = None, language: Optional[str] = None):
        super().__init__(code=1003, message=message, status_code=403, data=data, language=language)


class NotFoundError(APIException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在", data: Any = None, language: Optional[str] = None):
        super().__init__(code=1004, message=message, status_code=404, data=data, language=language)


class ServerError(APIException):
    """服务器内部错误"""
    def __init__(self, message: str = "服务器内部错误", data: Any = None, language: Optional[str] = None):
        super().__init__(code=1005, message=message, status_code=500, data=data, language=language)


class ForeignKeyViolationError(APIException):
    """外键约束冲突"""
    def __init__(
        self, 
        message: str = "该记录已关联其他资源，请先将其标记为'停用'以对用户隐藏", 
        data: Any = None, 
        language: Optional[str] = None
    ):
        super().__init__(code=1006, message=message, status_code=400, data=data, language=language)
