# ONLY ADD *PUBLIC* SETTINGS IN THIS FILE

URL = "https://ask-lara.de"
DATABASE = './instance/lara.db'
DATABASE_CONNECTION = "sqlite:///instance/lara.db"
DEBUG = True
# VERBOSE = True
# LOG_FILE = "lara.log"
# LOG_DIR = "/var/log/lara"
CACHE_DRIVER = "app.cache.memory_buffer.MemoryBuffer"
CACHE_TIMEOUT_INTERVAL = 3600

HOST = "0.0.0.0"
PORT = 8000

OFFLINE = False
PERIODIC_SPACING = 5

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 50000

ORGANIZAION = "LaraTUB"
REPOSITORY = "test"
DAYS_BEFORE_DUE = 2
ISSUES_BEFORE_DUE = 4
