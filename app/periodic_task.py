import sys
import json
import time
import requests
import argparse
import multiprocessing
import pickle

import app
from app import manager
from app import log as logging

LOG = logging.getLogger(__name__)

def produce_milestone(periodic_spacing=app.application.config.get("PERIODIC_SPACING", 3600)):
    while True:
        start_at = time.time()
        manager.pull_milestone()
        LOG.debug("pull milestone from github successfully.")
        end_at = time.time()

        elpase = end_at - start_at
        if elpase > periodic_spacing:
            continue
        else:
            time.sleep(periodic_spacing - elpase)


def consume_milestone(periodic_spacing=app.application.config.get("PERIODIC_SPACING", 5), timeout=None):
    counter = 0
    queue = manager.get_queue()

    while True:
        milestone = queue.get(block=True)
        milestone = pickle.loads(milestone)
        LOG.debug("Get milestone from queue, left size is %s." % queue.qsize())
        incoming_url = app.application.config['SLACK_APP_INCOMING_URL']
        text = dict(
            title=milestone.title,
            due_on=milestone.due_on.strftime("%Y-%m-%d %H:%M:%S")
        )
        data = {"text": json.dumps(text)}

        requests.post(incoming_url, data=json.dumps(data))
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
        LOG.debug("Server runs at address: 127.0.0.1, port: 50000")
        server = manager.get_server()
        server.serve_forever()
