import queue
import multiprocessing

from app import log as logging
from app.objects import get_git_object
# from app.broker import get_broker_handler, QueueManager

LOG = logging.getLogger(__name__)


def pull_milestone(github_login=None):
    name = "repository"
    if github_login:
        name = "{}:{}".format(github_login, name)

    repo = get_git_object(name)
    repo.get_milestone(github_login)



from queue import Queue
from multiprocessing.managers import BaseManager


BROKER = None
def get_broker_handler():
    global BROKER
    if not BROKER:
        BROKER = Queue()
    return BROKER


class QueueManager(BaseManager):
    pass


QueueManager.register('get_queue', callable=lambda:get_broker_handler())


MANAGER = None

def _get_manager():
    global MANAGER
    if not MANAGER:
        MANAGER = QueueManager(address=('127.0.0.1', 50000), authkey=b'default')

    return MANAGER


def get_server():
    m = _get_manager()
    server = m.get_server()
    return server


def get_queue():
    m = _get_manager()
    m.connect()
    q = m.get_queue()
    return q
