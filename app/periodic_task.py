import sys
import time
import argparse
import pickle
import datetime
import multiprocessing

import app
from app import manager
from app import log as logging
from app.objects import get_git_object
from app.db import api as dbapi

LOG = logging.getLogger(__name__)


def produce_milestone(periodic_spacing=app.application.config.get("PERIODIC_SPACING", 3600)):
    queue = manager.get_queue()
    while not queue.empty():
        queue.get(block=False)

    LOG.debug("Number of message remained in queue %s" % queue.qsize())
    milestones = dbapi.milestone_get_all()
    LOG.debug("Total milestones %s." % milestones.count())
    for milestone in milestones:
        LOG.debug("Put milestone *%s* into queue." % milestone.title)
        queue.put(pickle.dumps(milestone))
        time.sleep(1)

    while True:
        start_at = time.time()
        try:
            manager.pull_milestone()
        except ConnectionRefusedError:
            LOG.debug("The broker server is down.")
            # TODO: put milestone cached in database into queue again

        LOG.debug("pull milestone from github successfully.")
        end_at = time.time()

        elpase = end_at - start_at
        if elpase > periodic_spacing:
            continue
        else:
            time.sleep(periodic_spacing - elpase)


def consume_milestone(
        periodic_spacing=app.application.config.get("CONSUME_PERIODIC_SPACING", 5),
        time_delta=app.application.config.get("DAYS_BEFORE_DUE", 2),
        timeout=None):
    queue = manager.get_queue()

    while True:
        milestone = queue.get(block=True)
        milestone = pickle.loads(milestone)
        LOG.debug("Get milestone from queue, left size is %s." % queue.qsize())
        if milestone.due_on > datetime.datetime.utcnow() + datetime.timedelta(days=time_delta):
            LOG.debug("Due on %s. No need to inform developer." % milestone.due_on)
            continue
        if milestone.due_on < datetime.datetime.utcnow():
            dbapi.milestone_delete(milestone.id)
            LOG.debug("Due on %s. No need to inform developer. Remove it from database." % milestone.due_on)
            continue

        manager.alert_due_on_milestone(milestone)
        time.sleep(periodic_spacing)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--produce", dest="produce",
                        action="store_true",
                        required=False,
                        default=False)
    parser.add_argument("--consume", dest="consume",
                        action="store_true",
                        required=False,
                        default=False)
    parser.add_argument("--server", dest="server",
                        action="store_true",
                        required=False,
                        default=False)

    argv = parser.parse_args(sys.argv[1:])

    if argv.produce:
        LOG.debug("Going to produce milestone...")
        produce_milestone()
    elif argv.consume:
        LOG.debug("Going to consume milestone...")
        consume_milestone()
    elif argv.server:
        LOG.debug("Server runs at address: %s, port: %s" %
                  (app.application.config.get("BROKER_HOST", "127.0.0.1"),
                   app.application.config.get("BROKER_PORT", 50000)))
        server = manager.get_server()
        server.serve_forever()
