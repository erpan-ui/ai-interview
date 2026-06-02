from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
from typing import Optional, Any, Type
from functools import wraps
import re


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseResponseSchema(BaseSchema):
    id: int
    created_at: datetime = Field(default=0)
    updated_at: datetime = Field(default=0)

    def set_padded_id(self, pad_length: int = 4):
        """设置当前对象的padded_id"""
        if self.id is not None:
            self.padded_id = str(self.id).zfill(pad_length)
        return self

    def process_nested_padded_ids(self, pad_length: int = 4):
        """处理当前对象及其所有嵌套对象的padded_id"""
        # 处理当前对象
        self.set_padded_id(pad_length)
        
        # 遍历所有字段查找嵌套对象
        for field_name, field_value in self.__dict__.items():
            # 跳过特殊字段
            if field_name.startswith('_'):
                continue
                
            # 处理嵌套BaseResponseSchema对象
            if isinstance(field_value, BaseResponseSchema):
                field_value.process_nested_padded_ids(pad_length)
                
            # 处理嵌套列表
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, BaseResponseSchema):
                        item.process_nested_padded_ids(pad_length)
        
        return self


def format_datetime(dt: Optional[datetime]) -> str:
    """将datetime对象转换为ISO格式字符串，None转为空字符串"""
    if dt is None:
        return ""
    return dt.isoformat()


def to_timestamp(v: Any) -> int:
    """将各种时间格式转换为时间戳整数，None转为0"""
    if isinstance(v, datetime):
        return int(v.timestamp())
    elif v is None:
        return 0
    try:
        return int(v)
    except (TypeError, ValueError):
        raise ValueError("time fields must be valid datetime or a number")


def add_padded_id(pad_length: int = 4):
    """
    为Pydantic模型添加填充ID处理的装饰器
    
    Args:
        pad_length (int, optional): ID填充长度. 默认为4.
    
    Returns:
        装饰后的响应模型类
    """
    def decorator(cls: Type):
        # 动态添加padded_id字段
        if not hasattr(cls, 'padded_id'):
            cls.padded_id = Field(default=None, init=False)
        
        # 定义格式化方法
        def format_padded_id(id: int) -> str:
            """将ID转换为指定长度的填充字符串"""
            return str(id).zfill(pad_length)
        
        # 保存格式化方法
        setattr(cls, 'format_padded_id', staticmethod(format_padded_id))
        
        # 修改model_validate方法
        original_validate = getattr(cls, 'model_validate', None)
        
        @classmethod
        @wraps(original_validate or (lambda cls, obj: cls.model_construct(**obj.__dict__)))
        def enhanced_validate(cls, obj: Any):
            # 调用原始的验证方法
            if original_validate and original_validate != enhanced_validate:
                instance = original_validate(obj)
            else:
                instance = cls.model_construct(**obj.__dict__)
            
            # 动态设置padded_id
            padded_id_method = getattr(cls, 'format_padded_id', None)
            if padded_id_method:
                instance.padded_id = padded_id_method(instance.id)
            
            return instance
        
        # 更新类的model_validate方法
        cls.model_validate = enhanced_validate
        
        return cls
    
    return decorator
