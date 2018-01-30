from lara import log as logging
from lara import exceptions
from base import BaseCache

LOG = logging.getLogger(__name__)

class MemoryBuffer(BaseCache):

    def __init__(self):
        self._buffer_pool = dict()

    def __getitem__(self, key):
        return self._buffer_pool[key]

    def __setitem__(self, key, value):
        self._buffer_pool[key] = value

    def __del__(self, key):
        del self._buffer_pool[key]

    @property
    def keys(self):
        return self._buffer_pool.keys()

    @property
    def values(self):
        return self._buffer_pool.values()

    @property
    def items(self):
        return self._buffer_pool.items()
