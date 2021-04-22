from django.template.loader import render_to_string

from src.apis.tasks.email import send_verify_email
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings


class BaseNotification:
    """
    Base class for all notification related work
    """

    # email subject
    email_subject_template = None

    # email html template
    email_body_template = None

    def __init__(self, context=None):
        self.context = context or {}

    def send_mail(self, to):
        subject = self.email_subject_template.format(**self.context)
        body = render_to_string(self.email_body_template, context=self.context)
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to],
        )
