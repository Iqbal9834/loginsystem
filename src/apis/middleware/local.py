"""
Based on https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/local.py
Copyright (c) 2013 by the Werkzeug Team, see
https://github.com/mitsuhiko/werkzeug/blob/master/AUTHORS for more details.
"""

__all__ = ["Local", "release_local", "get_local"]

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        # noinspection PyCompatibility
        from thread import get_ident
    except ImportError:
        # noinspection PyCompatibility
        from _thread import get_ident


class Local(object):
    __slots__ = ("__storage__", "__ident_func__")

    def __init__(self):
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __init_local__(self):
        self.__storage__[self.__ident_func__()] = {}

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        # Since we are local, the storage is not initialize upon init on
        # object (which is shared) but on first set attribute *in* thread.
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)


def get_local(local):
    # Since we are local, the storage is not initialize upon init on
    # object (which is shared) but on first access *in* thread.
    try:
        return local.__storage__[local.__ident_func__()]
    except KeyError:
        local.__init_local__()
        return local.__storage__[local.__ident_func__()]


def release_local(local):
    local.__release_local__()
