from typing import Optional
import asyncio
from email.message import EmailMessage
import aiosmtplib
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("emailer")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10),
       retry=retry_if_exception_type((aiosmtplib.errors.SMTPException, ConnectionError)))
async def send_email(to_email: str, subject: str, body: str, html: Optional[str] = None) -> None:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info("Email sent", to=to_email, subject=subject)
    except Exception:
        logger.exception("Failed to send email")
        raise
