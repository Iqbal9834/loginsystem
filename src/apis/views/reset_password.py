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


class ResetPasswordSerializer(BaseSerializer):
    token = CharField()
    password = PasswordField()

    def to_internal_value(self, data):
        if "token " and "password" not in data:
            raise ValidationError("token and password  field is required ")
        return data

    def validate(self, attrs):
        token = attrs["token"]

        try:
            user = User.objects.get(token=token)
        except ObjectDoesNotExist:
            print("User not exists for token {0}".format(token))
            raise ValidationError("Token is invalid or expired")

        if user.token_expired:
            raise ValidationError("Token is invalid or expired")

        attrs["user"] = user
        return attrs

    def save(self, data):
        user = data["user"]
        raw_password = data["password"]

        update_fields = user.reset_password(raw_password)
        user.save(update_fields=update_fields)


class ResetPasswordView(MethodSerializerMixin, GenericAPIView):
    method_serializer_classes = {
        ("POST",): ResetPasswordSerializer,
    }

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_400_BAD_REQUEST],
        throttle_scope="reset_password_fail",
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer: ResetPasswordSerializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    create_response(
                        False,
                        err_name="BAD_REQUEST",
                        err_message=serializer.errors,
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            validate_data = serializer.validate(request.data)
            serializer.save(validate_data)
            return Response(
                create_response(
                    True,
                    data={"message": "Password has been successfully changed"},
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
