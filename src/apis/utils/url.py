from urllib.parse import (
    parse_qs,
    urlencode,
    urljoin,
    urlparse,
    urlsplit,
    urlunsplit,
)

from django.conf import settings


def build_url(url, path_params=None, query_params=None):
    """Given a URL, set or replace a path and query parameters and return the
    modified URL.

    >>> build_url('http://example.com?foo=bar&biz=baz', query_params={'foo',
    'stuff'})
    'http://example.com?foo=stuff&biz=baz'

    """
    url_no_qs, _, query_string = str(url).partition("?")
    try:
        url_no_qs = str(url_no_qs).format(**(path_params or {}))
    except KeyError as e:
        raise Exception("Missing %s key in path_params" % str(e)) from None
    try:
        query_string = str(query_string).format(**(query_params or {}))
    except KeyError as e:
        raise Exception("Missing %s key in query_params" % str(e)) from None
    scheme, netloc, path, _, fragment = urlsplit(url_no_qs)
    query_params = {**(query_params or {}), **parse_qs(query_string)}
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def absolute_uri(root_url, url):
    return urljoin(root_url.rstrip("/") + "/", url.lstrip("/"))


def absolute_app_uri(url=None):
    root_url = getattr(settings, "APP_ROOT_URL")
    if not url:
        return root_url
    return absolute_uri(root_url, url)


def absolute_api_uri(url=None):
    root_url = getattr(settings, "API_ROOT_URL")
    if not url:
        return root_url
    return absolute_uri(root_url, url)


def build_app_absolute_uri(url, path_params=None, query_params=None):
    return absolute_app_uri(url=build_url(url, path_params, query_params))


def build_api_absolute_uri(url, path_params=None, query_params=None):
    return absolute_api_uri(url=build_url(url, path_params, query_params))


def origin_from_url(url):
    if not url:
        return url
    url = urlparse(url)
    return "%s://%s" % (url.scheme, url.netloc)
