"""
验证码邮件派发：开发环境同步发送，生产环境走 Celery。
"""
import logging

from app.core.config import settings
from app.services.client.email_templates import client_email_service

logger = logging.getLogger(__name__)

# 本地 Redis 5.x 与新版 redis-py 需使用 RESP2
_REDIS_POOL_KWARGS = {"protocol": 2}


async def dispatch_verification_email(
    email: str,
    verification_code: str,
    code_type: str,
    user_name: str | None = None,
) -> None:
    """按环境派发验证码邮件。"""
    if settings.ENV == "development":
        # 开发环境不依赖 Celery Worker，同步尝试发信；失败则打印验证码便于调试
        try:
            if code_type == "registration":
                await client_email_service.send_registration_verification(
                    email, verification_code, user_name
                )
            elif code_type == "password-reset":
                await client_email_service.send_password_reset_code(
                    email, verification_code, user_name
                )
            else:
                raise ValueError(f"不支持的 code_type: {code_type}")
        except Exception as exc:
            logger.warning(
                "开发环境邮件发送失败（可忽略，本地通常未启动 SMTP）: %s | 邮箱=%s 验证码=%s",
                exc,
                email,
                verification_code,
            )
        return

    from app.schedule.jobs.email_tasks import send_verification_email_task

    send_verification_email_task.delay(
        email,
        verification_code,
        code_type,
        user_name,
    )


def configure_celery_redis_compat(celery_app) -> None:
    """为 Celery 的 Redis 连接启用 RESP2，兼容 Redis 5.x。"""
    celery_app.conf.update(
        broker_transport_options={"connection_pool_kwargs": _REDIS_POOL_KWARGS},
        result_backend_transport_options={"connection_pool_kwargs": _REDIS_POOL_KWARGS},
    )
