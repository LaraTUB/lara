import threading
from lara import application
from lara import log as logging

LOG = logging.getLogger(__name__)


class HyperCache():
    """ A thread-safe cache with a timer to process cache data after an interval
    A hyper cache will call a `handler` after an interval to process the data you put inside the cache-backend.
    """
    def __init__(self, driver, interval=application.config.get("CACHE_TIMEOUT_INTERVAL", 60), *args, **kwargs):
        self._buffer = driver(*args, **kwargs)
        self._timers = dict()
        self._interval = interval
        self._lock = threading.Lock()

    def set(self, key, value, handler=None, *func_args, **func_kwargs):
        self._lock.acquire()
        try:
            self._buffer[key] = value
            # TODO: may be useful while trigger the specific event
            # always set the key as `_event_cached_value` so that
            # we can distinguish it when performing the action
            # func_kwargs["_event_cached_value"] = value
            if handler:
                if self._timers.get(key):
                    self._timers[key].cancel()

                self._timers[key] = threading.Timer(self._interval, handler, *func_args, **func_kwargs)
                self._timers[key].start()
        finally:
            self._lock.release()

    def get(self, key):
        return self._buffer.get(key, None)

    def delete(self, key):
        self._lock.acquire()
        try:
            self._buffer.pop(key, None)
            timer = self._timers.pop(key, None)
            if timer:
                timer.cancel()
        finally:
            self._lock.release()
