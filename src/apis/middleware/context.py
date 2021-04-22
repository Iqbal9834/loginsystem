from functools import partial

from .local import Local, get_local, release_local

__all__ = [
    "get_request_context",
    "clear_request_context",
    "request_context",
    "task_context",
    "get_task_context",
    "clear_task_context",
    "get_from_context",
    "copy_dict_to_context",
]

# a Threaded local storage for storing request context assuming each request
# is fulfilled by one separate thread
request_context = Local()

get_request_context = partial(get_local, request_context)
clear_request_context = partial(release_local, request_context)

# a Threaded local storage for storing celery task context assuming each
# task is running by one separate thread
task_context = Local()

get_task_context = partial(get_local, task_context)
clear_task_context = partial(release_local, task_context)


def get_from_context(key: str):
    try:
        return getattr(request_context, key)
    except AttributeError:
        pass

    try:
        return getattr(task_context, key)
    except AttributeError:
        pass
    return None


def copy_dict_to_context(data: dict, context: Local):
    assert isinstance(data, dict), '"data" should be of type dict '
    for k, v in data.items():
        setattr(context, k, v)
