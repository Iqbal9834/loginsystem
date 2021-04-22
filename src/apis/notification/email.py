from src.apis.notification.base import BaseNotification


class EmailVerificationNotification(BaseNotification):
    email_subject_template = "Verify your email"
    email_body_template = "emails/email_verify.txt"


class PasswordResetNotification(BaseNotification):
    email_subject_template = "Reset your password"
    email_body_template = "auth/password_reset.txt"
