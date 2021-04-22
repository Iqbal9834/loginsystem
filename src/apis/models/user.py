import uuid
from datetime import timedelta


from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models, IntegrityError, transaction
from django.core.validators import validate_email
from django.db.models import CharField, DateTimeField, EmailField
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string


from src.apis.utils.url import build_app_absolute_uri
from src.apis import jwt
from src.apis.utils.utils import (
    has_any_uppercase_character,
    add_update_fields_to_save_kwargs,
)
from src.apis.notification import (
    EmailVerificationNotification,
    PasswordResetNotification,
)

__all__ = ["User"]

VERIFY_EMAIL_HOURS_VALID = 48
RESET_PASSWORD_HOURS_VALID = 48

CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class User(AbstractUser):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = EmailField(_("email address"), validators=[validate_email], unique=True)
    mobile_number = CharField(
        _("Mobile number"),
        max_length=18,
        unique=True,
    )
    # verification tokens
    token = CharField(max_length=32, null=True, blank=True, db_index=True)
    token_expires_at = DateTimeField(default=None, null=True, blank=True)

    email_verified = models.BooleanField(_("email verified"), default=False)
    address = CharField(max_length=100)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @classmethod
    def normalize_email(cls, email):
        email = cls.objects.normalize_email(email)
        return str(email).strip(" ").lower()

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.id and self.password:
            self.set_password(self.password)

        if has_any_uppercase_character(self.email):
            self.email = self.email.lower()
            self.username = self.email
            add_update_fields_to_save_kwargs(kwargs, ["email", "username"])

        if not self.username:
            self.username = self.email

        if not self.is_superuser and self.username != self.email:
            raise Exception("Username should always be same as email")

        return super().save(*args, **kwargs)

    def set_password(self, raw_password):
        super().set_password(raw_password)
        update_fields = ["password"]
        return update_fields

    @classmethod
    def create_app_user(cls, email, first_name, last_name, address, password, mobile_number):
        """
        Create an app user for given email and set given password
        :param email:
        :param password:
        :return:
        """
        try:
            email = cls.normalize_email(email)

            with transaction.atomic():
                user = cls(email=email,first_name=first_name, last_name=last_name, address=address, password=password, mobile_number=mobile_number)
                user.save()
        except IntegrityError:
            return None
        else:
            return user

    def get_display_name(self):
        return self.name or self.username or self.email

    def get_signup_response(self):
        response_data = {
            "id": self.id,
            "uuid":  self.uuid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "mobile_number": self.mobile_number,
            "joined_date": self.date_joined,
            "address": self.address,
            "email_verified": self.email_verified,
        }
        return response_data

    def set_token(self):
        self.token = get_random_string(32, CHARACTERS)

    def refresh_verify_email_expires_at(self):
        now = timezone.now()
        self.token_expires_at = now + timedelta(hours=VERIFY_EMAIL_HOURS_VALID)

    @property
    def token_expired(self):
        if self.token_expires_at > timezone.now():
            return False
        return True

    def generate_email_verification_token(self, save=False):
        self.set_token()
        self.refresh_verify_email_expires_at()
        if save:
            self.save(update_fields=["token", "token_expires_at"])

    def get_email_verification_link(self):
        if not self.token:
            return None
        return build_app_absolute_uri(
            settings.APP_USER_VERIFY_EMAIL_URL_PATH,
            # we can put token placeholder in path or query
            path_params={"token": self.token},
            query_params={"token": self.token},
        )

    def send_verify_email_mail(self):

        context = {
            "user": self,
            "url": self.get_email_verification_link(),
            "url_expiry_hours": VERIFY_EMAIL_HOURS_VALID,
        }
        notification = EmailVerificationNotification(context=context)
        email = self.email
        try:
            notification.send_mail(to=[email])
            print(f"Email Verification mail sent to user {email}")
        except Exception as e:
            print(e)

    def verify_email(self):
        self.email_verified = True
        self.token = None
        self.token_expires_at = None
        self.save(update_fields=["token", "token_expires_at", "email_verified"])

    @classmethod
    def get_user_for_mobile_number(cls, mobile_number, **filter_kwargs):

        mobile_number = mobile_number or filter_kwargs.pop("mobile_number", None)
        try:
            return User.objects.get(mobile_number=mobile_number, **filter_kwargs)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None

    def get_reset_password_link(self):
        if not self.token:
            return None
        return build_app_absolute_uri(
            settings.APP_USER_RESET_PASSWORD_URL_PATH,
            # we can put token placeholder in path or query
            path_params={"token": self.token},
            query_params={"token": self.token},
        )

    def send_reset_password_mail(self, request):

        context = {
            "user": self,
            "url": self.get_reset_password_link(),
            "datetime": timezone.now(),
            "ip_address": get_client_ip(request)[0],
        }
        notification = PasswordResetNotification(context=context)
        try:
            notification.send_mail(to=[self.email])
            print("Reset password mail sent to user %s" % (self.email))
        except Exception as e:
            print(e)

    def refresh_reset_password_expires_at(self):
        now = timezone.now()
        self.token_expires_at = now + timedelta(hours=RESET_PASSWORD_HOURS_VALID)

    def regenerate_reset_password_token(self, save=False):
        self.set_token()
        self.refresh_reset_password_expires_at()
        if save:
            self.save(update_fields=["token", "token_expires_at"])

    def set_password(self, raw_password):
        super().set_password(raw_password)
        update_fields = [
            "password",
        ]
        return update_fields

    def reset_password(self, raw_password):
        fields_updated = self.set_password(raw_password)
        self.token = None
        self.token_expires_at = None
        fields_updated += ("token", "token_expires_at")
        return fields_updated