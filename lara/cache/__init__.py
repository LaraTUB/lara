import importlib

from lara import application
from lara.cache import hyper_cache


cache_driver_name = application.config.get("CACHE_DRIVER",
                                   "lara.cache.memory_buffer.MemoryBuffer")

def _load_class(name=cache_driver_name):
    ind = name.rfind(".")
    module_name, klass_name = name[:ind], name[ind+1:]
    module = importlib.import_module(module_name)
    return getattr(module, klass_name)


def get_cache_handler(name=cache_driver_name):
    return hyper_cache.HyperCache(_load_class(name=name))
