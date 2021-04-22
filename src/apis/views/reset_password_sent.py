from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import CharField, EmailField
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import BaseSerializer, ValidationError

from src.apis.mixins.serializers_fields import PasswordField
from src.apis.mixins.view import MethodSerializerMixin
from src.apis.models import User
from src.apis.utils.throttels import ResponseStatusCodeThrottle
from src.apis.utils import create_response


class ResetPasswordEmailSerializer(BaseSerializer):
    email = EmailField()

    def validate(self, attrs):
        email = attrs["email"]
        email = str(email).strip().lower()
        user = None
        try:
            # user should be active and not superuser
            user = User.objects.get(email=email, is_active=True, is_superuser=False)
        except ObjectDoesNotExist:
            print("User %s is not found" % (email,))
        if user and not user.email_verified:
            raise ValidationError("Email %s is not verified." % email)
        attrs["user"] = user
        return attrs

    def save(self, data):
        request = self.context["request"]
        user = data["user"]

        if user is not None:
            user.regenerate_reset_password_token(save=True)
            user.send_reset_password_mail(request)


class EmailResetPasswordView(MethodSerializerMixin, GenericAPIView):
    method_serializer_classes = {
        ("POST",): ResetPasswordEmailSerializer,
    }

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_200_OK],
        throttle_scope="reset_password_email_success",
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        if "email" not in data:
            raise ValidationError("email field is required")
        try:

            serializer: ResetPasswordEmailSerializer = self.get_serializer(data=data)
            validate_data = serializer.validate(data)
            serializer.save(validate_data)
            return Response(
                create_response(
                    True,
                    data={
                        "message": "Mail has been sent successfully",
                    },
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                create_response(
                    False,
                    err_name="INTERNAL_SERVER_ERROR",
                    err_message="Something went wrong.",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
