import json
import random
from datetime import datetime, UTC
from typing import Optional, Dict
from app.services.common.redis import redis_client
from app.exceptions.http_exceptions import APIException
from app.core.config import settings


# 配置常量
VERIFICATION_CODE_EXPIRE = 600  # 10分钟
SEND_CODE_RATE_LIMIT = 60  # 1分钟发送限制
MAX_VERIFICATION_ATTEMPTS = 5  # 最大验证尝试次数


class RedisVerificationService:
    @staticmethod
    def generate_6_digit_code() -> str:
        """生成6位数字验证码"""
        return f"{random.randint(100000, 999999)}"

    @staticmethod
    async def generate_and_store_code(
        email: str,
        code_type: str,
        user_id: Optional[int] = None
    ) -> str:
        """生成验证码并存储到 Redis"""
        code = RedisVerificationService.generate_6_digit_code()
        key = f"verification_code:{code_type}:{email}"

        data = {
            "code": code,
            "user_id": user_id,
            "created_at": datetime.now(UTC).isoformat(),
            "attempts": 0
        }

        await redis_client.set_with_ttl(key, json.dumps(data), VERIFICATION_CODE_EXPIRE)
        return code

    @staticmethod
    async def verify_code(email: str, code: str, code_type: str) -> Dict:
        """验证验证码"""
        key = f"verification_code:{code_type}:{email}"
        data_str = await redis_client.get(key)

        if not data_str:
            raise APIException(status_code=400, message="验证码已过期或不存在")

        data = json.loads(data_str)

        # 检查尝试次数
        if data["attempts"] >= MAX_VERIFICATION_ATTEMPTS:
            await redis_client.delete(key)
            raise APIException(status_code=400, message="验证尝试次数过多，请重新获取验证码")

        # 验证码匹配
        if data["code"] != code:
            data["attempts"] += 1
            await redis_client.set_with_ttl(key, json.dumps(data), VERIFICATION_CODE_EXPIRE)
            raise APIException(status_code=400, message="验证码不正确")

        # 验证成功，删除验证码
        await redis_client.delete(key)
        return data

    @staticmethod
    async def check_send_rate_limit(email: str) -> bool:
        """检查发送频率限制"""
        key = f"verification_rate_limit:{email}"

        if await redis_client.check_cooldown(key):
            raise APIException(
                status_code=429,
                message="请稍后再试，每分钟只能发送一次验证码"
            )

        await redis_client.set_cooldown(key, SEND_CODE_RATE_LIMIT)
        return True

    @staticmethod
    async def clear_send_rate_limit(email: str) -> None:
        """清除发送频率限制（注册失败等场景下回滚）"""
        key = f"verification_rate_limit:{email}"
        await redis_client.delete(key)

    @staticmethod
    async def get_remaining_cooldown(email: str) -> int:
        """获取剩余冷却时间（秒）"""
        key = f"verification_rate_limit:{email}"
        ttl = await redis_client.redis.ttl(key)
        return max(0, ttl) if ttl > 0 else 0


redis_verification_service = RedisVerificationService()
