from .context import clear_request_context, get_request_context


class RequestContextMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        context = get_request_context()
        request.context = context
        response = self.get_response(request)
        clear_request_context()

        return response
