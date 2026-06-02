from fastapi import APIRouter
from app.schemas.response import ApiResponse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


# 创建PDF并在后台处理
@router.post("")
async def demo():
    return ApiResponse.success_without_data()
