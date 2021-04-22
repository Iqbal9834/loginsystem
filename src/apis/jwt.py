from datetime import datetime
from typing import Union
import jwt
from jwt.exceptions import InvalidTokenError
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import (
    jwt_encode_handler,
    jwt_get_secret_key,
    jwt_get_username_from_payload_handler,
    jwt_payload_handler,
)


def dt_to_epoch(dt: datetime) -> Union[int, None]:
    if isinstance(dt, datetime):
        return int(dt.timestamp())
    return None


__all__ = [
    "InvalidTokenError",
    "InvalidTokenType",
    "jwt_decode_handler",
    "generate_jwt_payload_for_user",
    "generate_jwt_auth_token_for_user",
    "generate_jwt_refresh_token_for_user",
    "verify_and_decode_auth_token",
    "verify_and_decode_refresh_token",
    "validate_jwt_token",
]


class InvalidTokenType(InvalidTokenError):
    pass


# override rest_framework_jwt.utils method, for options support
def jwt_decode_handler(token, options=None):
    if not options:
        options = {}
    options.setdefault("verify_exp", api_settings.JWT_VERIFY_EXPIRATION)
    # get user from token, BEFORE verification, to get user secret key
    unverified_payload = jwt.decode(token, None, False)
    secret_key = jwt_get_secret_key(unverified_payload)
    return jwt.decode(
        token,
        api_settings.JWT_PUBLIC_KEY or secret_key,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM],
    )


def generate_jwt_payload_for_user(user):
    payload = jwt_payload_handler(user)
    # drop email and user_id keys, Already deprecated in rest_framework_jwt
    del payload["user_id"]
    del payload["email"]
    return payload


def generate_jwt_auth_token_for_user(user):
    payload = generate_jwt_payload_for_user(user)
    payload["type"] = "bearer"
    token = jwt_encode_handler(payload)
    return token


def generate_jwt_refresh_token_for_user(user):
    payload = generate_jwt_payload_for_user(user)
    token_life_delta = api_settings.JWT_REFRESH_EXPIRATION_DELTA
    payload["exp"] = datetime.utcnow() + token_life_delta
    payload["type"] = "refresh"
    token = jwt_encode_handler(payload)
    return token


def verify_and_decode_auth_token(token, options=None):
    payload = jwt_decode_handler(token, options)
    token_type = payload.get("type")
    if token_type and token_type != "bearer":
        raise InvalidTokenType("Invalid token type for auth token")
    return payload


def verify_and_decode_refresh_token(token, options=None):
    payload = jwt_decode_handler(token, options)
    token_type = payload.get("type")
    if token_type and token_type != "refresh":
        raise InvalidTokenType("Invalid token type for refresh token")
    return payload


def validate_jwt_token(token, user=None):
    """
    Validate the given auth/refresh JWT token for given user. It run all
    security checks to invalidate token if required like
    1. User is not active
    2. Password reset of user

    :param token:
    :param user:
    :return: an user instance
    """
    # TODO : refactor this method
    # it's unverified payload
    payload = jwt.decode(token, None, False)
    username = jwt_get_username_from_payload_handler(payload)

    if username is None:
        raise InvalidTokenError(
            "'username' field value in token payload is null or not set"
        )

    if user is None:
        from src.apis.models.user import User
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            raise InvalidTokenError(f"No user found for username '{username}'")

    if getattr(user, "username") != username:
        raise InvalidTokenError(
            "'username' in token payload and subject user instance is not " "matched"
        )

    # ----------- 1) User account is set inactive ---------------------------
    if not user.is_active:
        raise InvalidTokenError("Invalid token")

    # ----------- 2) User changed password ----------------------------------
    # Invalidate the token, if user's password is changed after token is
    # issued
    token_iat = payload.get("orig_iat")  # time is in epoch
    # user_password_changed_at = dt_to_epoch(user.last_password_change)
    # if user_password_changed_at and user_password_changed_at > token_iat:
    #     raise InvalidTokenError("Invalid token")

    return user
