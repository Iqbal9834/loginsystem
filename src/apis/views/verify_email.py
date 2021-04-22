from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import CharField
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import BaseSerializer, ValidationError

from src.apis.models import User
from src.apis.utils import create_response, ResponseStatusCodeThrottle


class EmailVerificationSerializer(BaseSerializer):
    token = CharField(max_length=255)

    def is_valid(self, raise_exception=False):
        pass

    def to_internal_value(self, data):
        value = str(data)
        return value.strip()

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

    def save(self, attrs):
        user = attrs["user"]
        user.verify_email()


class EmailVerificationView(GenericAPIView):
    serializer_class = EmailVerificationSerializer

    @ResponseStatusCodeThrottle(
        status_codes=[status.HTTP_400_BAD_REQUEST],
        throttle_scope="verify_email_fail",
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            if "token" not in data:
                raise ValidationError(" token field required ")
            serializer = self.get_serializer(data=data)
            serializer.is_valid()
            attrs = serializer.validate(data)
            serializer.save(attrs)
            return Response(
                create_response(
                    True, data={"message": "Email is verified successfully"}
                ),
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                create_response(
                    False,
                    err_name="BAD_REQUEST",
                    err_message=e.detail,
                ),
                status=status.HTTP_400_BAD_REQUEST,
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
