from typing import TypeVar, Generic, Optional, Any, List, Dict, Callable
from fastapi import Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from math import ceil
from sqlalchemy import func, select
from sqlalchemy.orm import Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.exceptions.http_exceptions import APIException

T = TypeVar('T')


class PaginatedData(BaseModel, Generic[T]):
    """分页数据结构"""
    items: List[T]
    total: int
    per_page: int
    current_page: int
    last_page: int
    has_more: bool


class ApiResponse:
    """API 响应处理类"""

    @staticmethod
    def success(
            data: Any = None,
            message: str = "Success",
            body_code: int = 200,  # 业务成功码，0 表示成功
            http_code: int = status.HTTP_200_OK,
            headers: Dict = None
    ) -> JSONResponse:
        """成功响应"""
        response_data = {
            "code": body_code,  # 业务码
            "message": message,
            "data": jsonable_encoder(data) if data is not None else None
        }
        return JSONResponse(
            content=response_data,
            status_code=http_code,
            headers=headers
        )

    @staticmethod
    def success_without_data(
            http_code: int = status.HTTP_204_NO_CONTENT,
            headers: Dict = None
    ) -> Response:
        """无数据的成功响应"""
        return Response(status_code=http_code, headers=headers)

    @staticmethod
    def failed(
            message: str,
            body_code: int,
            http_code: int = status.HTTP_400_BAD_REQUEST,
            data: Any = None,
            headers: Dict = None
    ) -> JSONResponse:
        """失败响应"""
        response_data = {
            "code": body_code,
            "message": message
        }
        if data is not None:  # 仅当 data 不为 None 时添加该字段
            response_data["data"] = jsonable_encoder(data)
        return JSONResponse(
            content=response_data,
            status_code=http_code,
            headers=headers
        )

    async def paginate(
        db: AsyncSession,
        query,
        page: int = 1,
        per_page: int = 10,
        transform_func: Optional[Callable[[List[Any]], List[Any]]] = None,
        message: str = "Success",
        body_code: int = 200,
        http_code: int = status.HTTP_200_OK,
        headers: Dict = None
    ) -> JSONResponse:
        """优化的分页响应方法"""
        # 输入验证
        if page < 1 or per_page < 1:
            raise APIException(status_code=400, message="无效的分页参数")
        
        # 优化总数查询
        total_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(total_query)
        
        # 计算分页参数
        last_page = ceil(total / per_page) if per_page > 0 else 0
        
        # 验证页码是否超出范围
        if page > last_page and last_page > 0:
            raise APIException(status_code=404, message="页码不存在")
        
        # 执行分页查询
        offset_query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(offset_query)
        items = result.scalars().all()
        
        # 可选的数据转换
        if transform_func is not None:
            items = transform_func(items)
        
        # 构建分页数据
        paginated_data = PaginatedData(
            items=items,
            total=total,
            per_page=per_page,
            current_page=page,
            last_page=last_page,
            has_more=page < last_page
        )
        
        return JSONResponse(
            content={
                "code": body_code,
                "message": message,
                "data": jsonable_encoder(paginated_data)
            },
            status_code=http_code,
            headers=headers
        )
