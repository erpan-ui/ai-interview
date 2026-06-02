"""
邮件发送异步任务
"""
from app.core.celery_app import celery_app
from app.services.client.email_templates import client_email_service


@celery_app.task(bind=True, max_retries=3)
def send_verification_email_task(self, email: str, verification_code: str, code_type: str, user_name: str = None):
    """
    异步发送验证码邮件

    Args:
        email: 收件人邮箱
        verification_code: 验证码
        code_type: 验证码类型 ('registration' 或 'password-reset')
        user_name: 用户名
    """
    try:
        import asyncio

        if code_type == "registration":
            asyncio.run(client_email_service.send_registration_verification(
                email, verification_code, user_name
            ))
        elif code_type == "password-reset":
            asyncio.run(client_email_service.send_password_reset_code(
                email, verification_code, user_name
            ))
        else:
            raise ValueError(f"不支持的 code_type: {code_type}")

        return {"status": "success", "email": email, "code_type": code_type}

    except Exception as exc:
        # 记录错误
        print(f"邮件发送失败: {str(exc)}")

        # 重试机制
        if self.request.retries < self.max_retries:
            # 延迟重试：第1次60秒后，第2次120秒后，第3次180秒后
            countdown = 60 * (self.request.retries + 1)
            self.retry(countdown=countdown, exc=exc)

        # 所有重试用尽后抛出异常
        raise exc


@celery_app.task
def send_welcome_email_task(email: str, user_name: str):
    """
    发送欢迎邮件任务（可选，未来扩展）

    Args:
        email: 收件人邮箱
        user_name: 用户名
    """
    # TODO: 实现欢迎邮件发送逻辑
    print(f"欢迎邮件任务 {email} ({user_name}) - 尚未实现")
    return {"status": "not_implemented", "email": email, "user_name": user_name}


@celery_app.task(bind=True, max_retries=3)
def send_waiting_list_verification_task(self, email: str, verification_token: str, first_name: str = None):
    """
    异步发送等待列表验证邮件

    Args:
        email: 收件人邮箱
        verification_token: JWT 验证令牌
        first_name: 用户名
    """
    try:
        import asyncio

        asyncio.run(client_email_service.send_waiting_list_verification(
            email, verification_token, first_name
        ))

        return {"status": "success", "email": email, "type": "waiting_list_verification"}

    except Exception as exc:
        print(f"等待列表验证邮件发送失败: {str(exc)}")

        if self.request.retries < self.max_retries:
            countdown = 60 * (self.request.retries + 1)
            self.retry(countdown=countdown, exc=exc)

        raise exc


@celery_app.task(bind=True, max_retries=3)
def send_waiting_list_admin_notification_task(self, submission_data: dict):
    """
    异步发送等待列表管理员通知邮件

    Args:
        submission_data: 提交数据，包含 first_name、last_name、email、university
    """
    try:
        import asyncio

        asyncio.run(client_email_service.send_waiting_list_admin_notification(
            submission_data
        ))

        return {"status": "success", "email": submission_data.get("email"), "type": "admin_notification"}

    except Exception as exc:
        print(f"管理员通知邮件发送失败: {str(exc)}")

        if self.request.retries < self.max_retries:
            countdown = 60 * (self.request.retries + 1)
            self.retry(countdown=countdown, exc=exc)

        raise exc
