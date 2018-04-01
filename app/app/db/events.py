import pickle

from sqlalchemy import event
from app import models
from app import log as logging
from app.manager import get_queue

LOG = logging.getLogger(__name__)


@event.listens_for(models.MileStone, "after_insert")
def milestone_receive_after_insert(mapper, connection, target):
    queue = get_queue()
    queue.put(pickle.dumps(target))

    LOG.debug("Put milestone %s into broker, size is %s. " % (target.id, queue.qsize()))
