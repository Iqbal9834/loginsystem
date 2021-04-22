from celery.decorators import task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@task(name="user_email_verify")
def send_verify_email(subject, body, to):
    email = EmailMultiAlternatives(
        subject=subject, body=body, from_email=settings.EMAIL_HOST_USER, to=to
    )
    email.attach_alternative(body, "text/html")
    email.send(fail_silently=True)