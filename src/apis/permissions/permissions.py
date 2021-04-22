from copy import deepcopy

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import (
    BasePermission,
    DjangoModelPermissions,
    IsAuthenticated,
)

__all__ = [
    "IsAuthenticated",
    "IsAuthorized",
    "IsAuthenticatedAndAuthorized",
    "IsAuthorizedDjangoModelPermissions",
]


class IsAuthorized(BasePermission):
    """
    Allows access only to authorized users (i.e user have all permissions
    defined in view)
    """

    def get_required_permissions(self, view):
        if view.permission_required is None:
            raise ImproperlyConfigured(
                "{0} is missing the permission_required attribute. "
                "Define {0}.permission_required".format(view.__class__.__name__)
            )
        if isinstance(view.permission_required, str):
            perms = (view.permission_required,)
        else:
            perms = view.permission_required
        assert isinstance(perms, (list, tuple)), (
            "permission_required " "should be string, list or " "tuple"
        )
        return perms

    def has_permission(self, request, view):
        perms = self.get_required_permissions(view)
        return request.user.has_perms(perms)


class IsAuthenticatedAndAuthorized(BasePermission):
    """
    Allows access only to authenticated and authorized users (i.e user have all
    permissions defined in view)
    """

    authenticator_cls = IsAuthenticated
    authorizer_cls = IsAuthorized

    def has_permission(self, request, view):
        # first do authentication check
        is_authenticated = self.authenticator_cls().has_permission(request, view)
        if not is_authenticated:
            return False

        # then, do permission authorization check
        is_authorized = self.authorizer_cls().has_permission(request, view)
        if not is_authorized:
            return False

        return True


def _merge_view_perms_map(self, view):
    view_perms_map = getattr(view, "perms_map", {})
    self.perms_map = deepcopy(self.perms_map)
    self.perms_map.update(view_perms_map)


class IsAuthorizedDjangoModelPermissions(DjangoModelPermissions):
    """
    Allows access only to authorized users who have all permissions defined
    for each HTTP method in below default map or overridden in view.

    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """

    perms_map = {
        "GET": [],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": [],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view):
        _merge_view_perms_map(self, view)
        return super(IsAuthorizedDjangoModelPermissions, self).has_permission(
            request, view
        )
