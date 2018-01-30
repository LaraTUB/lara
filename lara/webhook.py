from github.PaginatedList import PaginatedList
from lara import app
import log as logging
from clients import GithubClient
from flask import request
from flask import jsonify
import json
import exceptions
import trigger
import utils
from objects import get_git_object

user = GithubClient.get_user()
__login__ = user.login

LOG = logging.getLogger(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    LOG.debug("Request from dialogflow is: %s" % req)
    kwargs = utils.merge_parameters(req["result"]["parameters"])

    if req["result"]["action"]:
        name, action = req["result"]["action"].split("_")
    else:
        name, action = kwargs.pop("action", "").split("_")

    LOG.debug("Request for github object *%s*, play *%s* action" % (name, action))
    LOG.debug("Request parameters are %s" % kwargs)

    results = dispatch_request(name, action, **kwargs)
    return jsonify(results)


def dispatch_request(name, action, **kwargs):
    action = "list" if (action == "*") else action

    handler = getattr(get_git_object(name), action)
    try:
        results = handler(**kwargs)
    except exceptions.RepositoryNotProvidedException:
        LOG.debug("Trigger Repository Missing Event.")
        followup_event = trigger.repository_missing_event(action="{}_{}".format(name, action), **kwargs)
        return build_response(**followup_event)
    except exceptions.IssueCommentNotFinishedException:
        LOG.debug("Trigger Issue Comemnt Not Finished Event.")
        followup_event = trigger.issue_comment_not_finished_event(action="{}_{}".format(name, action), **kwargs)
        return build_response(**followup_event)
    except exceptions.IssueIdNotProvidedException:
        LOG.error("Issue id not provided.")
    # except:
    #     raise exceptions.LaraException()

    return build_response(speech=results)


def build_response(**kwargs):
    speech = kwargs.pop("speech", "")
    displayText = kwargs.pop("displayText", speech)

    response = dict(
        speech=json.dumps(speech),
        displayText=json.dumps(displayText),
        source="Lara/lara backend"
    )

    response.update(kwargs)
    LOG.debug(response)
    return response
