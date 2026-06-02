"""
SMTP邮件发送服务
支持使用自定义SMTP服务器发送邮件
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Template
from app.core.config import settings
from app.services.common.thread_pool import thread_pool_service


class EmailTemplateLoader:
    """邮件模板加载器"""

    TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "resources" / "emails" / "auth"

    @classmethod
    def load_template(cls, template_name: str) -> Template:
        """
        加载邮件模板

        Args:
            template_name: 模板文件名（不含.html后缀）

        Returns:
            Jinja2 Template对象
        """
        template_path = cls.TEMPLATE_DIR / f"{template_name}.html"

        if not template_path.exists():
            raise FileNotFoundError(f"邮件模板未找到: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return Template(template_content)

    @classmethod
    def render_template(cls, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染邮件模板

        Args:
            template_name: 模板文件名
            context: 模板变量字典

        Returns:
            渲染后的HTML内容
        """
        template = cls.load_template(template_name)
        return template.render(**context)


def _send_email_sync(
    to_emails: List[str],
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    同步发送邮件（在线程池中执行）

    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        html_content: HTML邮件内容
        from_email: 发件人邮箱（默认使用配置中的邮箱）
        from_name: 发件人名称（默认使用配置中的名称）

    Returns:
        发送结果字典
    """
    # 使用配置中的默认值
    sender_email = from_email or settings.MAIL_FROM_ADDRESS
    sender_name = from_name or settings.MAIL_FROM_NAME

    # 创建邮件对象
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = f"{sender_name} <{sender_email}>"
    message['To'] = ', '.join(to_emails)

    # 添加HTML内容
    html_part = MIMEText(html_content, 'html', 'utf-8')
    message.attach(html_part)

    try:
        # 连接SMTP服务器
        # ssl: 使用SSL加密（端口465）
        # tls/starttls: 使用STARTTLS加密（端口587）
        if settings.MAIL_ENCRYPTION.lower() == 'ssl':
            # 使用SSL加密
            server = smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT)
        else:
            # 使用普通SMTP或TLS
            server = smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT)
            if settings.MAIL_ENCRYPTION.lower() in ['tls', 'starttls']:
                server.starttls()

        # 启用调试输出
        server.set_debuglevel(1)

        # 登录
        if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            print(f"SMTP 登录成功: {settings.MAIL_USERNAME}")

        # 发送邮件
        result = server.send_message(message)
        print(f"SMTP 发送结果: {result}")
        print(f"邮件已从 {settings.MAIL_FROM_ADDRESS} 发送至 {to_emails}")
        server.quit()

        return {
            "success": True,
            "message": "邮件发送成功",
            "to": to_emails
        }

    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP 认证失败: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

    except smtplib.SMTPException as e:
        error_msg = f"SMTP 错误: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

    except Exception as e:
        error_msg = f"邮件发送失败: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)


async def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    异步发送邮件

    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        html_content: HTML邮件内容
        from_email: 发件人邮箱
        from_name: 发件人名称

    Returns:
        发送结果字典
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        thread_pool_service.get_executor(),
        _send_email_sync,
        to_emails,
        subject,
        html_content,
        from_email,
        from_name
    )


async def send_template_email(
    to_emails: List[str],
    template_name: str,
    context: Dict[str, Any],
    subject: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用模板发送邮件

    Args:
        to_emails: 收件人邮箱列表
        template_name: 模板文件名（不含.html后缀）
        context: 模板变量字典
        subject: 邮件主题
        from_email: 发件人邮箱
        from_name: 发件人名称

    Returns:
        发送结果字典
    """
    # 渲染模板
    html_content = EmailTemplateLoader.render_template(template_name, context)

    # 发送邮件
    return await send_email(
        to_emails=to_emails,
        subject=subject,
        html_content=html_content,
        from_email=from_email,
        from_name=from_name
    )


async def send_verification_email(
    email: str,
    verification_code: str,
    first_name: str = "User",
    expires_minutes: int = 10
) -> Dict[str, Any]:
    """
    发送注册验证码邮件

    Args:
        email: 收件人邮箱
        verification_code: 验证码
        first_name: 用户名
        expires_minutes: 验证码过期时间（分钟）

    Returns:
        发送结果字典
    """
    return await send_template_email(
        to_emails=[email],
        template_name="registration_verification",
        context={
            "first_name": first_name,
            "verification_code": verification_code,
            "expires_minutes": expires_minutes
        },
        subject="Verify Your Email - Prepwise"
    )


async def send_password_reset_email(
    email: str,
    verification_code: str,
    first_name: str = "User",
    expires_minutes: int = 10
) -> Dict[str, Any]:
    """
    发送密码重置验证码邮件

    Args:
        email: 收件人邮箱
        verification_code: 验证码
        first_name: 用户名
        expires_minutes: 验证码过期时间（分钟）

    Returns:
        发送结果字典
    """
    return await send_template_email(
        to_emails=[email],
        template_name="password_reset",
        context={
            "first_name": first_name,
            "verification_code": verification_code,
            "expires_minutes": expires_minutes
        },
        subject="Password Reset Code - Prepwise"
    )


async def send_welcome_email(
    email: str,
    first_name: str = "User",
    dashboard_url: str = "https://prepwise.com/dashboard"
) -> Dict[str, Any]:
    """
    发送欢迎邮件

    Args:
        email: 收件人邮箱
        first_name: 用户名
        dashboard_url: 仪表盘 URL

    Returns:
        发送结果字典
    """
    return await send_template_email(
        to_emails=[email],
        template_name="welcome",
        context={
            "first_name": first_name,
            "dashboard_url": dashboard_url
        },
        subject="Welcome to Prepwise!"
    )


async def send_waiting_list_verification_email(
    email: str,
    verification_token: str,
    first_name: str = "User"
) -> Dict[str, Any]:
    """
    发送等待列表邮箱验证

    Args:
        email: 收件人邮箱
        verification_token: JWT 验证令牌
        first_name: 用户名

    Returns:
        发送结果字典
    """
    verification_link = f"{settings.FRONTEND_URL}/waiting-list/verify?token={verification_token}"

    return await send_template_email(
        to_emails=[email],
        template_name="waiting_list_verification",
        context={
            "first_name": first_name,
            "verification_link": verification_link
        },
        subject="Verify Your Email – Prepwise"
    )


async def send_waiting_list_admin_notification(
    submission_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    发送等待列表提交通知给管理员

    Args:
        submission_data: 提交数据，包含 first_name、last_name、email、university

    Returns:
        发送结果字典
    """
    return await send_template_email(
        to_emails=[settings.ADMIN_EMAIL],
        template_name="waiting_list_admin_notification",
        context={
            "first_name": submission_data.get("first_name"),
            "last_name": submission_data.get("last_name"),
            "email": submission_data.get("email"),
            "university": submission_data.get("university", "Not provided"),
            "verified_at": submission_data.get("verified_at")
        },
        subject="New Waiting List Submission - Prepwise"
    )