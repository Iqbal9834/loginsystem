from django.contrib.auth.models import AnonymousUser
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from rest_framework_jwt.authentication import JSONWebTokenAuthentication


from src.apis.jwt import (
    InvalidTokenError,
    InvalidTokenType,
    validate_jwt_token,
    verify_and_decode_auth_token,
)


class JSONWebTokenAuthenticationFromQueryParam(JSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "auth_token"
    HTTP query param. For example:
        /url-here?auth_token=eyJhbGciOiAiSFMyNTYiLCAidHlwIj

    View class should set `allow_query_param_auth` as True for using this
    middleware. By default this authentication is disabled for all views.
    """

    def get_jwt_value(self, request):
        try:
            match = resolve(request.path)
        except Resolver404:
            return None

        allow_query_param_auth = getattr(
            match.func.cls, "allow_query_param_auth", False
        )
        if not allow_query_param_auth:
            return None
        auth_token = request.GET.get("auth_token")
        return auth_token


def get_user_jwt(request):  # noqa: C901
    """
    Replacement for django session auth get_user & auth.get_user
     JSON Web Token authentication. Inspects the token for the user_id,
     attempts to get that user from the DB & assigns the user on the
     request object. Otherwise it defaults to AnonymousUser.

    This will work with existing decorators like LoginRequired  ;)

    Returns: instance of user object or AnonymousUser object
    """
    user = None
    drf_request = Request(request)

    try:
        # First try header based authentication
        user_jwt = JSONWebTokenAuthentication().authenticate(drf_request)
        # If still not found user, then try query param based authentication if
        # applicable as per view config
        if user_jwt is None:
            user_jwt = JSONWebTokenAuthenticationFromQueryParam().authenticate(
                drf_request
            )

        if user_jwt is not None:
            jwt_token = user_jwt[1]
            try:
                verify_and_decode_auth_token(jwt_token)
                # store the first part from the tuple (user, obj)
                user = user_jwt[0]
            except InvalidTokenType:
                pass
    except Exception:
        pass

    return user or AnonymousUser()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """ Middleware for authenticating JSON Web Tokens in Authorize Header """

    def process_request(self, request):
        # Only do JWT authentication, if no valid authenticated user is yet
        # founded and attached to `request.user`
        if isinstance(request.user, AnonymousUser):
            request.user = SimpleLazyObject(lambda: get_user_jwt(request))
            # we also have to exempt the CSRF view check for JWT
            # authenticated views
            request._dont_enforce_csrf_checks = True


class JWTValidationMiddleware(MiddlewareMixin):
    """
    A middleware that do extra validation of token assuming token is valid
    with all required fields in payload and user is authenticated. If token is
    found invalid then it sets `request.user` to AnonymousUser, so that
    following middleware's and view can found request as unauthenticated.

    It's recommended to put this middleware after
    `JWTAuthenticationMiddleware` in `MIDDLEWARE` section of settings.
    """

    def process_request(self, request):
        try:
            auth_token = JSONWebTokenAuthentication().get_jwt_value(Request(request))
            user = request.user
        except AuthenticationFailed:
            return None

        if auth_token is None or not user.is_authenticated:
            return
        try:
            validate_jwt_token(auth_token, user=user)
        except InvalidTokenError:
            request.user = SimpleLazyObject(lambda: AnonymousUser())


class ApiKeyAuthentication(BaseAuthentication):
    www_authenticate_realm = "api"

    def get_api_key(self, request):
        api_key_header = request.META.get("HTTP_X_API_KEY")
        api_key_param = request.query_params.get("api_key")
        return api_key_header or api_key_param

    def authenticate(self, request):
        api_key = self.get_api_key(request)
        if not api_key:
            return None
        return self.authenticate_credentials(api_key)

    def authenticate_credentials(self, api_key):
        pass
        # try:
        #     org_config = OrganizationConfig.objects.get(api_key=api_key)
        # except OrganizationConfig.DoesNotExist:
        #     raise AuthenticationFailed(_("Invalid API key"))

        # organization = org_config.organization
        # if not features.has("organizations:api-keys", organization):
        #     raise AuthenticationFailed(_("Invalid API key"))

        # try:
        #     org_member = OrganizationMember.objects.get(
        #         organization=organization, is_super_admin=True
        #     )
        # except OrganizationMember.DoesNotExist:
        #     raise Exception(f"Super admin for the {organization} not found")
        # user = org_member.user
        # return user, api_key

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm
