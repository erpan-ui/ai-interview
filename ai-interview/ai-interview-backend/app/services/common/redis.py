from redis.asyncio import Redis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        # 构建Redis连接参数
        redis_params = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "decode_responses": True
        }
        
        # 只有当密码不为空时才添加密码参数
        if hasattr(settings, "REDIS_PASSWORD") and settings.REDIS_PASSWORD:
            redis_params["password"] = settings.REDIS_PASSWORD

        # 本地 Redis 5.x 不支持 RESP3 的 HELLO 命令，需使用协议 2
        redis_params["protocol"] = 2

        self.redis = Redis(**redis_params)

    async def set_with_ttl(self, key: str, value: str, ttl_seconds: int):
        """设置键值对，带过期时间"""
        await self.redis.setex(key, ttl_seconds, value)

    async def get(self, key: str) -> str:
        """获取值"""
        return await self.redis.get(key)

    async def delete(self, key: str):
        """删除键"""
        await self.redis.delete(key)

    async def set_cooldown(self, key: str, ttl_seconds: int):
        """设置冷却时间"""
        await self.redis.setex(key, ttl_seconds, "1")

    async def check_cooldown(self, key: str) -> bool:
        """检查是否在冷却中"""
        return bool(await self.redis.exists(key))

    def pipeline(self, *args, **kwargs):
        """
        兼容原生redis-py的pipeline用法，直接转发到底层redis实例。
        注意：如果底层用的是redis.asyncio.Redis，返回的是异步pipeline。
        """
        return self.redis.pipeline(*args, **kwargs)

    async def brpop(self, key, timeout=1):
        return await self.redis.brpop(key, timeout=timeout)

    async def close(self):
        """关闭Redis连接"""
        await self.redis.close()


redis_client = RedisClient()
