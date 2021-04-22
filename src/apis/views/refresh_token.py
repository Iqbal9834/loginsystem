from django.conf import settings
from django.utils import timezone
from jwt.exceptions import InvalidTokenError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from src.apis.jwt import (
    generate_jwt_auth_token_for_user,
    generate_jwt_refresh_token_for_user,
    validate_jwt_token,
    verify_and_decode_auth_token,
    verify_and_decode_refresh_token,
)
from src.apis.mixins.serializers import ViewRequestSerializer
from rest_framework.serializers import ValidationError, CharField
from src.apis.utils import create_response


class RefreshTokenSerializer(ViewRequestSerializer):
    bearer_token = CharField(required=False)
    auth_token = CharField(required=False)
    refresh_token = CharField()

    def validate(self, attrs):
        auth_token = attrs.get("auth_token", attrs.get("bearer_token"))
        if not auth_token:
            raise ValidationError({"auth_token": "This field is required"})

        refresh_token = attrs["refresh_token"]
        try:
            print("Verifying and decoding auth token")
            # Don't do token expiration check, we will allow expired auth
            # token to be valid for getting new auth token until refresh
            # token is also valid and not expired
            auth_payload = verify_and_decode_auth_token(
                auth_token, options={"verify_exp": False}
            )
        except InvalidTokenError:
            print("Invalid auth token")
            raise ValidationError("Invalid auth token")

        try:
            print("Verifying and decoding refresh token")
            refresh_payload = verify_and_decode_refresh_token(refresh_token)
        except InvalidTokenError:
            print("Invalid/expired refresh token")
            raise ValidationError("Invalid/expired refresh token")

        if auth_payload["username"] != refresh_payload["username"]:
            print("Username mismatch in auth and refresh token")
            raise ValidationError("username is mismatch in tokens")

        try:
            user = validate_jwt_token(refresh_token)
        except InvalidTokenError:
            print("Invalid refresh token due to user changed password")
            raise ValidationError("Invalid/expired refresh token")

        attrs["user"] = user
        return attrs


class RefreshTokenView(GenericAPIView):
    """
    API View that returns a refreshed token (with new expiration) based on
    existing token
    """

    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer: RefreshTokenSerializer = self.get_serializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return Response(
                    create_response(
                        False, err_name="BAD_REQUEST", err_message=e.detail
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = serializer.validated_data.get("user")
            auth_token = generate_jwt_auth_token_for_user(user)
            refresh_token = generate_jwt_refresh_token_for_user(user)

            response_data = {
                "auth_token": auth_token,
                "auth_expires_in": getattr(settings, "AUTH_TOKEN_EXPIRATION"),
                "refresh_token": refresh_token,
                "refresh_expires_in": getattr(settings, "REFRESH_TOKEN_EXPIRATION"),
            }

            # update last login refresh of user
            user.save()
            print(f"Successfully issued new auth token for user {user}")

            response = Response(
                create_response(True, data=response_data),
                status=status.HTTP_200_OK,
            )
            return response
        except Exception as e:
            print(e)
            return Response(
                create_response(
                    False,
                    err_name="INTERNAL_SERVER_ERROR",
                    err_message="Internal server error",
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
