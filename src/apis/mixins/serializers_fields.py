from rest_framework.serializers import (
    CharField,
    DjangoValidationError,
    Field,
    ImageField,
    URLField,
    ValidationError,
    as_serializer_error,
    get_error_detail,
)
from django.contrib.auth.password_validation import (
    get_password_validators,
    validate_password,
)
from django.utils.translation import gettext_lazy as _


class PasswordField(CharField):
    MIN_LENGTH = 8
    MAX_LENGTH = 50

    def __init__(self, disable_validate_password=False, **kwargs):
        # min length validation will be managed by django validator
        kwargs["max_length"] = PasswordField.MAX_LENGTH
        kwargs["allow_blank"] = False
        kwargs["trim_whitespace"] = False
        super().__init__(**kwargs)
        self._django_validators = self.get_django_validators()

        # This will control the validation process of password related to
        # it's strength which we mostly do using django validators. If set
        # True, field will do necessary field label validations but not do
        # django password validation
        self.disable_validate_password = disable_validate_password

    def get_django_validators(self):
        validator_config = [
            {
                "NAME": "django.contrib.auth.password_validation"
                ".UserAttributeSimilarityValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation"
                ".MinimumLengthValidator",
                "OPTIONS": {"min_length": PasswordField.MIN_LENGTH},
            },
            {
                "NAME": "django.contrib.auth.password_validation"
                ".CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation"
                ".NumericPasswordValidator",
            },
        ]
        return get_password_validators(validator_config)

    def run_validators(self, value):
        # first run DRF serializer field validators
        super().run_validators(value)

        if self.disable_validate_password:
            return

        # then, do django based password validation
        try:
            user = self.context.get("user")
            validate_password(
                value, user=user, password_validators=self._django_validators
            )
        except DjangoValidationError as exc:
            raise ValidationError(get_error_detail(exc))


class MobileNumberField(CharField):
    """
    A mobile number field for doing format validation and also do calling
    code support check for system and return international formatted mobile
    number
    """

    default_error_messages = {
        "invalid_mobile_number": _("Not a valid mobile number."),
        "invalid_calling_code": _("Not a valid calling code in mobile number"),
        "system_not_support_calling_code": _(
            "Calling code {calling_code} is not supported by system"
        ),
        "invalid_mobile_number_length": _("Mobile number length is invalid"),
    }

    def __init__(self, **kwargs):
        self.cc_support_check = kwargs.pop("cc_support_check", True)
        super().__init__(**kwargs)

    def get_default_calling_code(self):
        pass

    def to_internal_value(self, data):
        mobile_number = data

        return mobile_number
