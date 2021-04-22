import inspect
from datetime import timedelta

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UserActiveMiddleware(MiddlewareMixin):
    disallowed_paths = ()

    def process_view(self, request, view_func, view_args, view_kwargs):
        view = view_func
        if not inspect.isfunction(view_func):
            view = view.__class__

        try:
            path = "%s.%s" % (view.__module__, view.__name__)
        except AttributeError:
            return

        if path.startswith(self.disallowed_paths):
            return

        if not request.user.is_authenticated:
            return
        request.user.save()
