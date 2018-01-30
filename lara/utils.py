from functools import wraps
import log as logging
from github.PaginatedList import PaginatedList
import json

LOG = logging.getLogger(__name__)


def merge_parameters(kwargs):
    parameters = dict()

    for key, value in kwargs.items():
        if key.startswith("last_"):
            key = key.split("_")[-1]
            if not parameters.get(key):
                parameters[key] = value
        else:
            parameters[key] = value

    return parameters


def serializer_fields(*args, **kwargs):

    def _extract(provided_keys, data):
        nested_keys = [key for key in provided_keys if key.find(".") != -1]
        keys = [key for key in provided_keys if key not in nested_keys]
        res = {k: v for k, v in data.items() if k in keys and data.get(k)}
        for key in nested_keys:
            # TODO: maybe here should handle cases like "user.*"
            # NOTE: only test two-level nested key
            k = key.split(".")[0]
            _provided_keys = (key.split(".")[1],)

            _data = data.get(k, None)

            if not _data:
                continue

            if isinstance(_data, dict):
                res.update({k: _extract(_provided_keys, _data)})
            elif isinstance(_data, list):
                res.update({k: [_extract(_provided_keys, d) for d in _data]})

        return res

    def decorator(func):
        @wraps(func)
        def wrapper(*arg, **kwarg):
            results = func(*arg, **kwarg)
            if isinstance(results, PaginatedList):
                d = [_extract(args, result._rawData) for result in results if hasattr(result, "_rawData")]
            elif hasattr(results, "_rawData"):
                d = _extract(args, results._rawData)
            else:
                d = dict()
            return d

        return wrapper

    return decorator


def filter_fields(**kwargs):
    pass



def get_desired_parameters(*args):
    def decorator(func):
        @wraps(func)
        def wrapper(*arg, **kwarg):
            desired_kwargs = {k:v for k, v in kwarg.items()
                              if args and k in args and kwarg.get(k, None)}
            return func(*arg, **desired_kwargs)

        return wrapper

    return decorator
