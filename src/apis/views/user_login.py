from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import EmailField, ValidationError, CharField

from src.apis.utils.throttels import ResponseStatusCodeThrottle
from src.apis.mixins.serializers_fields import PasswordField
from src.apis.mixins.serializers import ViewRequestSerializer
from src.apis.utils import create_response
from src.apis.jwt import (
    generate_jwt_auth_token_for_user,
    generate_jwt_refresh_token_for_user,
)
from src.apis.models import User
from src.apis.service import BaseOtpNotification


class InvalidCredentials(ValidationError):
    pass


class LoginEmailSerializer(ViewRequestSerializer):
    email = EmailField(max_length=100)
    password = PasswordField(disable_validate_password=True)

    def validate_email(self, email):
        return str(email).strip().lower()


class UserLoginView(GenericAPIView):
    serializer_class = LoginEmailSerializer

    @ResponseStatusCodeThrottle(
        status_codes=(status.HTTP_400_BAD_REQUEST,),
        throttle_scope="login_bad_attempt",
    )
    def post(self, request):
        try:
            data = request.data
            if not data:
                raise ValidationError("either email or mobile_number field is required")
            user = self.get_user_by_email_auth(request=request)
        except (ValidationError, InvalidCredentials) as e:
            return Response(
                create_response(False, err_name="BAD_REQUEST", err_message=e.detail),
                status=status.HTTP_400_BAD_REQUEST,
            )
        auth_token = generate_jwt_auth_token_for_user(user)
        refresh_token = generate_jwt_refresh_token_for_user(user)

        response_data = {
            "type": "bearer",
            "auth_token": auth_token,
            "auth_expires_in": getattr(settings, "AUTH_TOKEN_EXPIRATION"),
            "refresh_token": refresh_token,
            "refresh_expires_in": getattr(settings, "REFRESH_TOKEN_EXPIRATION"),
        }
        response = Response(
            create_response(True, data=response_data),
            status=status.HTTP_200_OK,
        )
        return response

    @staticmethod
    def get_user_by_email_auth(request):
        data = request.data
        serializer = LoginEmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        raw_password = serializer.data.get("password")
        print(f"Authenticating user for email {email}")
        user = authenticate(request, **{"username": email, "password": raw_password})
        if user is None:
            print(f"Bad authentication for email {email}")
            raise InvalidCredentials("Invalid email or password ")
        print(f"{user} is authenticated successfully")
        # if user.email_verified == False:
        #     raise ValidationError("User Email is not verified ")
        return user
