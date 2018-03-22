# ONLY ADD *PUBLIC* SETTINGS IN THIS FILE

URL = "https://ask-lara.de"
DATABASE = './instance/lara.db'
DATABASE_CONNECTION = "sqlite:///instance/lara.db"
DEBUG = True
VERBOSE = True
LOG_FILE = "lara.log"
# LOG_DIR = "/var/log/lara"
CACHE_DRIVER = "app.cache.memory_buffer.MemoryBuffer"
CACHE_TIMEOUT_INTERVAL = 60

HOST = "0.0.0.0"
PORT = 8000
