from uuid import uuid4

from django.conf import settings

from .context import request_context

DEFAULT_REQUEST_ID_HEADER_NAME = "HTTP_X_REQUEST_ID"
REQUEST_ID_HEADER = getattr(
    settings, "REQUEST_ID_HEADER", DEFAULT_REQUEST_ID_HEADER_NAME
)


def generate_request_id():
    return str(uuid4())


def get_request_id(request):
    if hasattr(request, "request_id"):
        return request.request_id
    elif REQUEST_ID_HEADER:
        return request.META.get(REQUEST_ID_HEADER, "")
    else:
        return generate_request_id()


def get_current_request_id():
    try:
        return request_context.request_id
    except AttributeError:
        return ""


class RequestIdMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        request_id = get_request_id(request)
        request.request_id = request_id
        request_context.request_id = request_id

        response = self.get_response(request)
        response["Request-Id"] = request_id

        return response
