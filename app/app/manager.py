import operator
import json
import uuid
import datetime
import requests

from queue import Queue
from multiprocessing.managers import BaseManager

from app import application
from app import log as logging
from app.objects import get_git_object
from app.db import api as dbapi


LOG = logging.getLogger(__name__)


BROKER = None
def get_broker_handler():
    global BROKER
    if not BROKER:
        BROKER = Queue()
    return BROKER


class QueueManager(BaseManager):
    pass


QueueManager.register('get_queue', callable=lambda:get_broker_handler())


def _get_manager(broker_host, broker_port, broker_authkey):
    return QueueManager(address=(broker_host, broker_port), authkey=broker_authkey)

def get_server():
    broker_host = application.config.get("BROKER_BIND_ADDRESS", "127.0.0.1")
    broker_port = application.config.get("BROKER_PORT", 50000)
    broker_authkey = application.config.get("BROKER_AUTHKEY", b'default')
    m = _get_manager(broker_host, broker_port, broker_authkey)
    server = m.get_server()
    return server


def get_queue():
    import os
    broker_host = application.config.get("BROKER_HOST", "127.0.0.1")
    broker_host = os.environ.get("BROKER_HOST") if os.environ.get("BROKER_HOST") else broker_host
    broker_port = application.config.get("BROKER_PORT", 50000)
    broker_authkey = application.config.get("BROKER_AUTHKEY", b'default')
    m = _get_manager(broker_host, broker_port, broker_authkey)
    m.connect()
    q = m.get_queue()
    return q


def pull_milestone(github_login=None):
    users = dbapi.user_get_all()

    for user in users:
        if not user.github_login:
            continue

        name = "{}:{}".format(user.github_login, "repository")

        repo = get_git_object(name)
        repo.get_milestone(user.github_login)


def alert_due_on_milestone(milestone):
    user = dbapi.user_get(milestone.user_id)
    github_login = user.github_login
    LOG.debug("Try to inform developer %s for coming milestone." % github_login)
    issue_obj = get_git_object("{}:issue".format(github_login))
    kwargs = {"repository": application.config['REPOSITORY'],
              "assignee.login": github_login,
              "session_id": "{}:{}".format(github_login, uuid.uuid4())}

    issues = issue_obj.list(**kwargs)
    text = None
    raw_data = json.loads(milestone.raw_data)
    if len(issues) < application.config.get("ISSUES_BEFORE_DUE", 4):
        text = "Milestone <{}|{}> is coming up, you've only got 2 more issues. Keep up the good work!".format(raw_data.get('html_url', ''), milestone.title)
    else:
        text = "It's only two days until Milestone <{}|{}> and you have {} open issues. Do you need any help working on these?".format(raw_data.get('html_url', ''),
                                                                                                                                       milestone.title,
                                                                                                                                       len(issues))
    try:
        incoming_url = application.config['SLACK_APP_INCOMING_URL'][user.slack_user_id]
    except KeyError:
        LOG.error("user %s isn't configured well." % user.github_login)
        incoming_url = application.config['SLACK_APP_INCOMING_URL'][application.config['DEFAULT_SLACK_CHANNEL']]
        text = "Hi {}. {}".format(user.github_login, text)

    data = {"text": text}
    requests.post(incoming_url, data=json.dumps(data))
    # Alerted developer, so safely remove it from cache
    dbapi.milestone_delete(milestone.id)


def find_colleagues_matching_skills(github_login):
    '''
    Lara will search for colleagues in the same repo with fewer open issues.
    '''
    users = dbapi.user_get_all()
    d = dict()
    for user in users:
        if user.github_login == github_login:
            continue
        github_login = user.github_login
        issue_obj = get_git_object("{}:issue".format(github_login))
        kwargs = {"repository": application.config['REPOSITORY'],
                  "assignee.login": github_login,
                  "session_id": "{}:{}".format(github_login, uuid.uuid4())}
        issues = issue_obj.list(**kwargs)
        count = len(issues)
        d[user.github_token] = count

    sorted_d = sorted(d.items(), key=operator.itemgetter(1))
    # return first k-th colleagues as choices
    if len(sorted_d) < application.config.get("FOUND_COLLEAGUES_COUNT", 3):
        return sorted_d
    return sorted_d[0:application.config.get("FOUND_COLLEAGUES_COUNT", 3)]
