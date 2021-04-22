from functools import wraps

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.serializers import ValidationError


def create_response(
    success, data=None, item=None, items=None, err_name=None, err_message=None
):
    if success:
        if data is not None:
            return {"success": True, "data": data}
        elif item is not None:
            return {"success": True, "data": {"item": item}}
        elif items is not None:
            return {"success": True, "data": {"items": items}}
    else:
        return {
            "success": False,
            "error": {"name": err_name, "message": err_message},
        }


def interval_server_error_response(e, view=None):
    return Response(
        create_response(
            False,
            err_name="INTERNAL_SERVER_ERROR",
            err_message="Something went wrong. Please try again later.",
        ),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def safe_view_request_handler(bad_request_errors=None):
    """
    A decorator to wrap a request method of class based view. This wrapper
    handles all basic exception handling and convert them to proper response
    with valid response status code.

    :param bad_request_errors: a tuple of exception/error classes to be
    consider for bad request type response. Error class instance should have
    `.detail` attribute for error message.
    :return:
    """
    if bad_request_errors is None:
        bad_request_errors = ()

    # we will add default drf ValidationError for bad request error
    bad_request_errors = (*bad_request_errors, ValidationError)

    def wrapped(method):
        @wraps(method)
        def wrapper(view, request, *args, **kwargs):
            try:
                response = method(view, request, *args, **kwargs)
                return response
            except bad_request_errors as e:
                return Response(
                    create_response(
                        False, err_name="BAD_REQUEST", err_message=e.detail
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Http404:
                return Response(
                    create_response(
                        False, err_name="NOT_FOUND", err_message="NO DETAIL"
                    ),
                    status=status.HTTP_404_NOT_FOUND,
                )
            except APIException as e:
                return Response(
                    create_response(
                        False,
                        err_name=e.__class__.__name__,
                        err_message=e.detail,
                    ),
                    status=e.status_code,
                )
            except Exception as e:
                return interval_server_error_response(e)

        return wrapper

    return wrapped
