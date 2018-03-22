from app import log as logging
from app import exceptions
from app.cache.base import BaseCache

LOG = logging.getLogger(__name__)

class MemoryBuffer(BaseCache):

    def __init__(self):
        self._buffer_pool = dict()

    def __getitem__(self, key):
        return self._buffer_pool[key]

    def __setitem__(self, key, value):
        self._buffer_pool[key] = value

    def __delitem__(self, key):
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


    def get(self, key, default=None):
        return self._buffer_pool.get(key, default)

    def pop(self, key, default=None):
        try:
            value = self.get(key, default)
            del self[key]
        except KeyError:
            LOG.debug("Key %s not found in MemoryBuffer." % key)
            pass

    def __repr__(self):
        return self._buffer_pool.__repr__()
