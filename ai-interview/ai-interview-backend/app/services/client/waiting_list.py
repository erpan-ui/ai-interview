from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, UTC
from app.models.waiting_list import WaitingList
from app.core.security import AuthBase
from app.core.config import settings
from app.db.session import transaction
from app.exceptions.http_exceptions import APIException
from app.services.common.redis import redis_client
from app.schedule.jobs.email_tasks import send_waiting_list_verification_task, send_waiting_list_admin_notification_task


class WaitingListService:
    @staticmethod
    async def generate_verification_token(email: str, waiting_list_id: int) -> str:
        from jose import jwt
        from datetime import datetime, UTC
        import uuid

        expire = datetime.now(UTC) + timedelta(hours=24)
        jti = str(uuid.uuid4())  # 唯一令牌标识符

        to_encode = {
            "sub": str(waiting_list_id),
            "email": email,
            "scope": "waiting-list-verification",
            "exp": expire,
            "jti": jti
        }

        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # 将当前有效令牌存储到 Redis
        redis_key = f"waiting_list:token:{email}"
        await redis_client.set_with_ttl(redis_key, jti, 24 * 3600)  # 24小时

        return token

    @staticmethod
    async def verify_token(token: str) -> Dict:
        payload = AuthBase.verify_token(token, scope="waiting-list-verification")
        if not payload:
            raise APIException(status_code=400, message="无效或已过期的验证链接")

        # 检查此令牌是否仍为该邮箱的当前有效令牌
        email = payload.get("email")
        jti = payload.get("jti")

        if email and jti:
            redis_key = f"waiting_list:token:{email}"
            current_jti = await redis_client.get(redis_key)

            if current_jti != jti:
                raise APIException(status_code=400, message="此验证链接已被更新的链接替代")

        return payload

    @staticmethod
    async def check_ip_rate_limit(ip_address: str) -> None:
        redis_key = f"waiting_list:ip:{ip_address}"
        count_str = await redis_client.get(redis_key)

        if count_str and int(count_str) >= 100:
            raise APIException(
                status_code=400,
                message="该 IP 地址请求过多，请1小时后再试"
            )

        if count_str:
            await redis_client.redis.incr(redis_key)
        else:
            await redis_client.set_with_ttl(redis_key, "1", 3600)

    @staticmethod
    async def submit_application(
        db: AsyncSession,
        data: Dict,
        ip_address: str,
        user_agent: str
    ) -> Dict:
        existing_query = select(WaitingList).where(WaitingList.email == data["email"])
        result = await db.execute(existing_query)
        existing = result.scalar_one_or_none()

        if existing and existing.is_verified:
            raise APIException(
                status_code=400,
                message="该邮箱已在等待列表中"
            )

        await WaitingListService.check_ip_rate_limit(ip_address)

        if existing and not existing.is_verified:
            token = await WaitingListService.generate_verification_token(
                data["email"],
                existing.id
            )
            send_waiting_list_verification_task.delay(
                data["email"],
                token,
                data["first_name"]
            )
            return {
                "email": data["email"],
                "message": "验证邮件已重新发送，请查收邮箱"
            }

        async with transaction(db):
            new_record = WaitingList(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                university=data.get("university"),
                ip_address=ip_address,
                user_agent=user_agent,
                is_verified=False
            )

            db.add(new_record)
            await db.flush()

            token = await WaitingListService.generate_verification_token(
                data["email"],
                new_record.id
            )

            send_waiting_list_verification_task.delay(
                data["email"],
                token,
                data["first_name"]
            )

            return {
                "email": data["email"],
                "message": "请查收邮箱进行验证"
            }

    @staticmethod
    async def verify_email(db: AsyncSession, token: str) -> Dict:
        payload = await WaitingListService.verify_token(token)
        waiting_list_id = int(payload.get("sub"))
        email = payload.get("email")

        async with transaction(db):
            query = select(WaitingList).where(WaitingList.id == waiting_list_id)
            result = await db.execute(query)
            record = result.scalar_one_or_none()

            if not record:
                raise APIException(status_code=404, message="等待列表记录不存在")

            if record.email != email:
                raise APIException(status_code=400, message="无效的验证链接")

            if record.is_verified:
                raise APIException(status_code=400, message="邮箱已验证")

            record.is_verified = True
            record.verified_at = datetime.now(UTC)

            # 从 Redis 清除验证令牌
            redis_key = f"waiting_list:token:{email}"
            await redis_client.delete(redis_key)

            send_waiting_list_admin_notification_task.delay({
                "first_name": record.first_name,
                "last_name": record.last_name,
                "email": record.email,
                "university": record.university,
                "verified_at": record.verified_at.isoformat()
            })

            return {
                "message": "邮箱验证成功",
                "email": record.email,
                "verified_at": record.verified_at
            }

    @staticmethod
    async def resend_verification(db: AsyncSession, email: str, ip_address: str) -> Dict:
        query = select(WaitingList).where(WaitingList.email == email)
        result = await db.execute(query)
        record = result.scalar_one_or_none()

        if not record:
            raise APIException(status_code=404, message="该邮箱不在等待列表中")

        if record.is_verified:
            raise APIException(status_code=400, message="该邮箱已验证")

        await WaitingListService.check_ip_rate_limit(ip_address)

        token = await WaitingListService.generate_verification_token(email, record.id)

        send_waiting_list_verification_task.delay(
            email,
            token,
            record.first_name
        )

        return {
            "message": "验证邮件已重新发送",
            "email": email
        }


waiting_list_service = WaitingListService()