# ADD *PUBLIC* SETTINGS IN THIS FILE

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
PERIODIC_SPACING = 86400
CONSUME_PERIODIC_SPACING = 5

# The IP where the broker service runs.
BROKER_HOST = "127.0.0.1"
# 0.0.0.0 means accept all clients' connection
BROKER_BIND_ADDRESS = "127.0.0.1"
BROKER_PORT = 50000

DEFAULT_SLACK_CHANNEL = 'test'

ORGANIZAION = "LaraTUB"
REPOSITORY = "test"
DAYS_BEFORE_DUE = 2
ISSUES_BEFORE_DUE = 4
FOUND_COLLEAGUES_COUNT = 3
