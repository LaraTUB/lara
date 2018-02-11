from lara import log as logging

LOG = logging.getLogger(__name__)


class BaseCache(object):

    def __init__(self):
        pass

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        return self
