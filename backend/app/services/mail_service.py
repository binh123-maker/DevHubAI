import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.auth.interfaces.mail import IMailService
from app.core.config import settings

logger = logging.getLogger(__name__)


class MailService(IMailService):
    """Transactional Mail Service supporting SMTP and fallback development logger (Parts 3 & 23)."""

    def _render_template(self, template_name: str, context: dict[str, Any]) -> tuple[str, str]:
        """Renders HTML and Text email templates based on template_name and context variables."""
        full_name = context.get("full_name", "DevHub AI User")
        otp_code = context.get("otp_code", "")
        ttl_minutes = context.get("ttl_minutes", 10)

        if template_name in ("forgot_password", "password_reset_otp", "otp_verification"):
            text_content = (
                f"Hello {full_name},\n\n"
                f"Your DevHub AI verification code is: {otp_code}\n"
                f"This code will expire in {ttl_minutes} minutes.\n\n"
                "If you did not request this code, please ignore this message.\n\n"
                "Best regards,\nDevHub AI Team"
            )
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
                .card {{ max-width: 480px; margin: 0 auto; background: #1e293b; border-radius: 20px; padding: 32px; border: 1px solid #334155; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }}
                .brand {{ font-size: 24px; font-weight: 800; color: #6366f1; text-align: center; margin-bottom: 24px; }}
                .otp-box {{ background: #0f172a; border-radius: 16px; padding: 20px; text-align: center; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #38bdf8; border: 1px solid #38bdf8; margin: 24px 0; }}
                .footer {{ text-align: center; font-size: 12px; color: #94a3b8; margin-top: 24px; }}
              </style>
            </head>
            <body>
              <div class="card">
                <div class="brand">DevHub AI</div>
                <h2>Mã xác thực của bạn</h2>
                <p>Xin chào <strong>{full_name}</strong>,</p>
                <p>Nhập mã xác thực bên dưới để tiếp tục quy trình khôi phục mật khẩu DevHub AI:</p>
                <div class="otp-box">{otp_code}</div>
                <p style="font-size: 13px; color: #cbd5e1;">Mã có hiệu lực trong vòng <strong>{ttl_minutes} phút</strong> và chỉ sử dụng được 1 lần.</p>
                <div class="footer">
                  <p>© 2026 DevHub AI. Built for Developers.</p>
                </div>
              </div>
            </body>
            </html>
            """
            return text_content, html_content

        elif template_name == "password_changed":
            text_content = (
                f"Hello {full_name},\n\n"
                "Your DevHub AI password was changed successfully.\n"
                "If you did not perform this action, please contact support immediately.\n\n"
                "Best regards,\nDevHub AI Team"
            )
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
                .card {{ max-width: 480px; margin: 0 auto; background: #1e293b; border-radius: 20px; padding: 32px; border: 1px solid #334155; }}
                .brand {{ font-size: 24px; font-weight: 800; color: #6366f1; text-align: center; margin-bottom: 24px; }}
                .alert {{ background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #34d399; padding: 16px; border-radius: 12px; margin: 16px 0; font-size: 14px; text-align: center; }}
              </style>
            </head>
            <body>
              <div class="card">
                <div class="brand">DevHub AI</div>
                <h2>Thông báo bảo mật</h2>
                <p>Xin chào <strong>{full_name}</strong>,</p>
                <div class="alert">✓ Mật khẩu tài khoản DevHub AI của bạn đã được thay đổi thành công.</div>
                <p style="font-size: 12px; color: #94a3b8;">Tất cả phiên đăng nhập khác trên các thiết bị đã tự động ngắt kết nối để đảm bảo an toàn.</p>
              </div>
            </body>
            </html>
            """
            return text_content, html_content

        # Fallback generic message
        return f"DevHub AI Notification: {template_name}", f"<h2>DevHub AI Notification</h2><p>{template_name}</p>"

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
