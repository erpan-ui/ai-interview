import asyncio
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings
from app.services.common.thread_pool import thread_pool_service

# 配置日志
logger = logging.getLogger("email_service")

# 配置 FastMail 连接
mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM_ADDRESS,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_ENCRYPTION.lower() == "tls" if hasattr(settings, "MAIL_ENCRYPTION") else False,
    MAIL_SSL_TLS=settings.MAIL_ENCRYPTION.lower() == "ssl" if hasattr(settings, "MAIL_ENCRYPTION") else False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# 初始化 FastMail
fastmail = FastMail(mail_conf)

# 设置模板目录
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "resources" / "emails"
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# 初始化 Jinja2 环境
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


class EmailService:
    """邮件服务类，提供邮件发送功能"""

    @staticmethod
    def _send_sync(
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """同步发送邮件"""
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        
        from_email = from_email or settings.MAIL_FROM_ADDRESS
        from_name = from_name or settings.MAIL_FROM_NAME
        
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = ", ".join(to_emails)

        part = MIMEText(html_content, "html")
        message.attach(part)

        try:
            with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
                # 如果需要 TLS 加密
                if hasattr(settings, "MAIL_ENCRYPTION") and settings.MAIL_ENCRYPTION.lower() == "tls":
                    server.starttls()

                # 如果需要登录
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                
                server.sendmail(from_email, to_emails, message.as_string())
                
            logger.info(f"邮件发送成功，收件人: {to_emails}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise

    @classmethod
    async def send(
        cls,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """异步发送邮件"""
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        
        try:
            # 确保 html_content 不为空
            if not html_content or len(html_content.strip()) == 0:
                logger.error("邮件 HTML 内容为空，发送失败")
                return False
        
            # 使用 FastMail 发送邮件（异步方式）
            message = MessageSchema(
                subject=subject,
                recipients=to_emails,
                body=html_content,  # 使用 body 参数
                subtype="html"
            )
        
            await fastmail.send_message(message)
            logger.info(f"异步邮件发送成功，收件人: {to_emails}")
            return True
        except Exception as e:
            logger.warning(f"FastMail 发送失败，尝试同步方式: {e}")
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                thread_pool_service.get_executor(), 
                cls._send_sync, to_emails, subject, html_content, from_email, from_name
            )

    @classmethod
    async def send_with_template(
        cls,
        to_emails: Union[str, List[str]],
        template_name: str,
        template_params: Dict[str, Any],
        subject: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        使用模板发送邮件

        参数:
        -----------
        to_emails: 收件人列表或单个收件人
        template_name: 模板名称（如 'auth/verification.html'）
        template_params: 模板参数
        subject: 邮件主题
        from_email: 发件人邮箱，默认使用配置值
        from_name: 发件人名称，默认使用配置值
        """
        try:
            # 添加默认参数
            params = {
                "img_host": settings.AWS_ENDPOINT if hasattr(settings, "AWS_ENDPOINT") else "",
                **template_params
            }
            
            # 渲染模板
            template = jinja_env.get_template(template_name)
            html_content = template.render(**params)
            # 发送邮件
            return await cls.send(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
                from_email=from_email,
                from_name=from_name
            )
        except Exception as e:
            logger.error(f"使用模板发送邮件失败: {e}")
            raise

    # 便捷方法
    @classmethod
    async def send_verification_email(cls, email: str, first_name: str, verification_code: str) -> bool:
        """发送账号验证邮件"""
        return await cls.send_with_template(
            to_emails=email,
            template_name="auth/verification.html",
            template_params={
                "first_name": first_name,
                "code": verification_code
            },
            subject="Bienvenue chez Moriarty - Activez votre compte"
        )

# 导出实例以便使用
email_service = EmailService()