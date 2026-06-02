import asyncio
from typing import TypeVar, Generic, Any, List, Dict, Callable, Type
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from math import ceil
from sqlalchemy import func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from sqlalchemy.engine.result import Row

T = TypeVar('T')

class Paginator(Generic[T]):
    """Laravel 风格的分页器"""

    def __init__(self, query: Select, db: AsyncSession):
        self.query = query
        self.db = db
        self._items = None
        self._total = None
        self._per_page = 10
        self._page = 1
        self._last_page = None
        self._processors = []
        self._result = None  # 保存原始查询结果
        
    async def paginate(self, page: int = 1, per_page: int = 10) -> 'Paginator':
        """执行分页查询"""
        self._page = max(1, page)
        self._per_page = max(1, per_page)
        
        # 计算总数
        if self._total is None:
            total_query = select(func.count()).select_from(self.query.subquery())
            self._total = await self.db.scalar(total_query)
            
        # 计算最后一页
        self._last_page = ceil(self._total / self._per_page) if self._per_page > 0 else 0
        
        # 应用分页
        paginated_query = self.query.offset((self._page - 1) * self._per_page).limit(self._per_page)
        
        # 执行查询
        self._result = await self.db.execute(paginated_query)
        
        # 区分单实体查询和多列查询
        keys = list(self._result.keys())  # 转为列表供后续使用
        if len(keys) == 1:
            # 单实体查询
            self._items = self._result.scalars().all()
        else:
            # 多列查询
            self._items = self._process_multi_column_result(keys)
            
        # 应用所有处理器（支持异步处理）
        for processor in self._processors:
            if asyncio.iscoroutinefunction(processor):
                self._items = await processor(self._items)
            else:
                self._items = processor(self._items)
            
        return self
    
    def _process_multi_column_result(self, keys: List[str]) -> List[Any]:
        """处理多列查询结果"""
        if not self._result:
            return []
        
        rows = self._result.all()
        if not rows:
            return []
        
        processed_items = []
        
        for row in rows:
            if isinstance(row, Row) or isinstance(row, tuple):
                # 获取主实体（第一列）
                main_entity = row[0]
                
                # 将附加列设置为主实体的属性
                for i in range(1, len(keys)):
                    # 使用列名作为属性名
                    attr_name = keys[i]
                    setattr(main_entity, attr_name, row[i])
                
                processed_items.append(main_entity)
            else:
                # 单列查询
                processed_items.append(row)
                
        return processed_items
    
    def process(self, callback: Callable[[List[Any]], List[Any]]) -> 'Paginator':
        """添加处理器函数"""
        self._processors.append(callback)
        return self
        
    def map(self, model_class: Type[BaseModel]) -> 'Paginator':
        """映射到 Pydantic 模型"""
        def mapper(items):
            mapped_items = []
            for item in items:
                # 提取实体属性
                item_dict = {}
                
                # 添加所有非内部属性
                for key, value in vars(item).items():
                    if not key.startswith('_'):
                        item_dict[key] = value
                
                # 处理关联对象
                for attr_name in dir(item):
                    if attr_name.startswith('_') or attr_name in item_dict:
                        continue
                    
                    try:
                        attr_value = getattr(item, attr_name)
                        # 检查是否为关联对象
                        if hasattr(attr_value, '__table__') or attr_name in model_class.__annotations__:
                            item_dict[attr_name] = attr_value
                    except Exception:
                        # 忽略不可访问的属性
                        pass
                
                # 尝试使用 model_validate 创建实例
                try:
                    mapped_item = model_class.model_validate(item_dict)
                except Exception as e:
                    # 备选方式：直接构造
                    mapped_item = model_class.model_construct(**item_dict)
                
                mapped_items.append(mapped_item)
            
            return mapped_items
        
        self._items = mapper(self._items)
        return self
    
    @property
    def items(self) -> List[Any]:
        """获取当前页数据"""
        return self._items or []
    
    @property
    def total(self) -> int:
        """获取总数"""
        return self._total or 0
    
    @property
    def per_page(self) -> int:
        """每页条数"""
        return self._per_page
    
    @property
    def current_page(self) -> int:
        """当前页码"""
        return self._page
    
    @property
    def last_page(self) -> int:
        """最后一页页码"""
        return self._last_page or 0
    
    @property
    def has_more(self) -> bool:
        """是否还有更多页"""
        return self._page < (self._last_page or 0)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "items": self.items,
            "total": self.total,
            "per_page": self.per_page,
            "current_page": self.current_page,
            "last_page": self.last_page,
            "has_more": self.has_more
        }
    
    def to_json(self) -> Dict:
        """转换为 JSON 可序列化字典"""
        return jsonable_encoder(self.to_dict())
    
    def response(self, message: str = "Success", code: int = 200, http_code: int = 200) -> JSONResponse:
        """创建 API 响应"""
        return JSONResponse(
            content={
                "code": code,
                "message": message,
                "data": self.to_json()
            },
            status_code=http_code
        )