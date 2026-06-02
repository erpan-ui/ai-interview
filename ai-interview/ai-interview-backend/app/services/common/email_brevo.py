import asyncio
from app.core.config import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from typing import Dict, Any, List, Optional
from app.services.common.thread_pool import thread_pool_service  # 导入线程池服务


def _send_verification_sync(email: str, verification_code: str):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    subject = "验证您的邮箱"
    html_content = f"""
    <html>
        <body>
            <h2>欢迎注册!</h2>
            <p>您的验证码是: <strong>{verification_code}</strong></p>
            <p>该验证码将在30分钟后失效。</p>
        </body>
    </html>
    """
    sender = {"name": settings.BREVO_EMAIL_FROM_NAME, "email": settings.BREVO_EMAIL_FROM}
    to = [{"email": email}]

    try:
        return api_instance.send_transac_email({
            "sender": sender,
            "to": to,
            "subject": subject,
            "htmlContent": html_content
        })
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        raise


async def send_verification_email(email: str, verification_code: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool_service.get_executor(), _send_verification_sync,
                                      email, verification_code)


async def send_template_email(
    to_emails: List[str],
    template_id: int,
    template_params: Optional[Dict[str, Any]] = None,
    subject: Optional[str] = None,
    sender: Optional[Dict[str, str]] = None
):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    if sender is None:
        sender = {"name": settings.BREVO_EMAIL_FROM_NAME, "email": settings.BREVO_EMAIL_FROM}
    to = [{"email": email} for email in to_emails]

    email_params = {
        "sender": sender,
        "to": to,
        "templateId": template_id,
    }
    if template_params:
        email_params["params"] = template_params
    if subject:
        email_params["subject"] = subject

    def _send_template_sync():
        try:
            return api_instance.send_transac_email(email_params)
        except ApiException as e:
            print(f"Exception when calling SMTPApi->send_transac_email: {e}")
            raise

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool_service.get_executor(), _send_template_sync)
