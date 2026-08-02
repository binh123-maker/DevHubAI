from enum import Enum
from typing import NamedTuple


class MailTemplateType(str, Enum):
    WELCOME = "welcome"
    EMAIL_VERIFICATION_OTP = "email_verification_otp"
    PASSWORD_RESET_OTP = "password_reset_otp"
    PASSWORD_CHANGED = "password_changed"
    EMAIL_CHANGED = "email_changed"
    GOOGLE_LINKED = "google_linked"
    GITHUB_LINKED = "github_linked"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_RECOVERY = "account_recovery"


class MailTemplateSpec(NamedTuple):
    template_type: MailTemplateType
    subject_template: str
    required_variables: list[str]
    default_locale: str = "en"


MAIL_TEMPLATES: dict[MailTemplateType, MailTemplateSpec] = {
    MailTemplateType.WELCOME: MailTemplateSpec(
        template_type=MailTemplateType.WELCOME,
        subject_template="Welcome to DevHub AI, {full_name}!",
        required_variables=["full_name"],
    ),
    MailTemplateType.EMAIL_VERIFICATION_OTP: MailTemplateSpec(
        template_type=MailTemplateType.EMAIL_VERIFICATION_OTP,
        subject_template="Your DevHub AI Verification Code: {otp_code}",
        required_variables=["otp_code", "ttl_minutes"],
    ),
    MailTemplateType.PASSWORD_RESET_OTP: MailTemplateSpec(
        template_type=MailTemplateType.PASSWORD_RESET_OTP,
        subject_template="Reset your DevHub AI Password",
        required_variables=["otp_code", "ttl_minutes"],
    ),
}
