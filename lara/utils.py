import six
import json
from functools import wraps
from copy import deepcopy
from datetime import datetime
from github.PaginatedList import PaginatedList
from lara import log as logging

LOG = logging.getLogger(__name__)


def extract_slack_parameters(req):
    slack = req.get("originalRequest", dict())
    if not slack:
        return slack

    kwargs = {
        "assignee.login": slack["data"]["event"]["user"],
        "team_id": slack["data"]["team_id"],
        "request_source": "slack"
    }

    return kwargs


def merge_parameters(req):
    kwargs = req["result"]["parameters"]
    parameters = dict()
    for key, value in kwargs.items():
        if key.startswith("last_"):
            key = key.split("_")[-1]
            if not parameters.get(key):
                parameters[key] = value
        else:
            parameters[key] = value

    parameters['session_id'] = req['sessionId']
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
        def wrapper(*func_args, **func_kwargs):
            results = func(*func_args, **func_kwargs)
            if isinstance(results, (PaginatedList, list)):
                # TODO: to retrive more pages if we cannot get expected data from
                # the first n pages.
                d = [_extract(args, result._rawData) for result in results if hasattr(result, "_rawData")]
            elif hasattr(results, "_rawData"):
                d = _extract(args, results._rawData)
            else:
                d = dict()
            return d

        return wrapper

    return decorator


def filter_fields(*args):
    # only test supporting two-level nested key
    def _filter(filter_kwargs, data):
        for key, value in filter_kwargs.items():
            # if users don't set the value for that key, pass through it without validation

            key = "number" if key == "id" else key
            # handle nested keys
            if key.find(".") != -1:
                ks = key.split(".")
                _data = deepcopy(data)
                for k in ks:
                    if isinstance(_data, list):
                        _data = [_d for _d in _data if getattr(_d, k)]
                    else:
                        _data = getattr(_data, k)
                    if not _data:
                        return None

                if isinstance(_data, list):
                    _data = [_d for _d in _data if _d == value]
                    if not _data:
                        return None
                elif _data != value:
                    return None

            elif not getattr(data, key):
                return None
            elif getattr(data, key) != value:
                return None

        return data

    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):

            results = func(*func_args, **func_kwargs)

            # NOTE: handle equal operation
            # only compare with `int`, `str`, no `datetime`
            filter_kwargs = {k:v for k, v in func_kwargs.items() if k in args and func_kwargs.get(k)}
            if filter_kwargs.get('id'):
                return results

            if isinstance(results, PaginatedList):
                d = list()
                for result in results:
                    dd = _filter(filter_kwargs, result)
                    if dd:
                        d.append(dd)

            else:
                d = _filter(filter_kwargs, results)

            # to avoid NoneType
            return d if d else None

        return wrapper
    return decorator


def get_desired_parameters(*args):
    def decorator(func):
        @wraps(func)
        def wrapper(*arg, **kwarg):
            desired_kwargs = {k:v for k, v in kwarg.items()
                              if args and k in args and kwarg.get(k, None)}
            if desired_kwargs.get('id') and not isinstance(desired_kwargs['id'], six.integer_types):
                desired_kwargs['id'] = int(desired_kwargs['id'])

            return func(*arg, **desired_kwargs)

        return wrapper

    return decorator


def make_datetime(since):
    if isinstance(since, six.string_types):
        return datetime.strptime(since, "%Y-%m-%d")
