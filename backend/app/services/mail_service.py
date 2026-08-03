import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.auth.interfaces.mail import IMailService
from app.core.config import settings

from pathlib import Path
import jinja2

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class MailService(IMailService):
    """Transactional Mail Service using Jinja2 templates and SMTP / Dev Log fallback."""

    def __init__(self) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            autoescape=True,
        )

    def _render_template(self, template_name: str, context: dict[str, Any]) -> tuple[str, str]:
        """Renders HTML and Text email templates using Jinja2 design system templates."""
        full_name = context.get("full_name", "DevHub AI User")
        otp_code = context.get("otp_code", "")
        ttl_minutes = context.get("ttl_minutes", 10)

        # Plain Text Fallback Rendering
        if template_name in ("forgot_password", "password_reset_otp", "otp_verification"):
            text_content = (
                f"Hello {full_name},\n\n"
                f"Your DevHub AI verification code is: {otp_code}\n"
                f"This code will expire in {ttl_minutes} minutes.\n\n"
                "Never share this code with anyone. DevHub AI staff will never ask for your OTP.\n\n"
                "If you did not request this code, please ignore this message.\n\n"
                "Best regards,\nDevHub AI Team"
            )
        elif template_name == "password_changed":
            text_content = (
                f"Hello {full_name},\n\n"
                "Your DevHub AI password was changed successfully.\n"
                "All other active login sessions have been invalidated for security.\n"
                "If you did not perform this action, please contact support immediately.\n\n"
                "Best regards,\nDevHub AI Team"
            )
        else:
            text_content = f"DevHub AI Notification: {template_name}\n\nHello {full_name}"

        # Jinja2 HTML Rendering
        template_map = {
            "forgot_password": "emails/forgot_password.html",
            "password_reset_otp": "emails/forgot_password.html",
            "otp_verification": "emails/otp_verification.html",
            "password_changed": "emails/password_changed.html",
        }
        template_file = template_map.get(template_name, f"emails/{template_name}.html")

        try:
            template = self.env.get_template(template_file)
            html_content = template.render(**context)
        except jinja2.TemplateNotFound:
            logger.warning(f"[MailService] Template '{template_file}' not found, falling back to base template.")
            template = self.env.get_template("emails/base.html")
            html_content = template.render(**context)

        return text_content, html_content

    async def send_mail(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_context: dict[str, Any],
    ) -> bool:
        text_content, html_content = this_render = self._render_template(template_name, template_context)

        logger.info(
            f"[MailService] Preparing email to={to_email}, subject='{subject}', template='{template_name}', context={template_context}"
        )

        # Check if SMTP is fully configured
        if settings.smtp_username and settings.smtp_password and settings.smtp_host != "localhost":
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.smtp_from_email
                msg["To"] = to_email

                part1 = MIMEText(text_content, "plain", "utf-8")
                part2 = MIMEText(html_content, "html", "utf-8")
                msg.attach(part1)
                msg.attach(part2)

                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                    if settings.smtp_tls:
                        server.starttls()
                    server.login(settings.smtp_username, settings.smtp_password)
                    server.sendmail(settings.smtp_from_email, [to_email], msg.as_string())

                logger.info(f"[MailService] Successfully sent SMTP email to {to_email}")
                return True
            except Exception as exc:
                logger.error(f"[MailService] Failed to send SMTP email to {to_email}: {exc}")
                # Fallthrough to dev log mode

        # Development Fallback Logger Mode
        print(f"\n==================== [DEV MAIL SENDER] ====================")
        print(f"TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{text_content}")
        print(f"===========================================================\n")
        return True


mail_service = MailService()
