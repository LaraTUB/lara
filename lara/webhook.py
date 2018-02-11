import json
from github.PaginatedList import PaginatedList

from flask import request
from flask import jsonify

from lara import application
from lara import exceptions
from lara import log as logging
from lara import trigger
from lara import utils
from lara.objects import get_git_object

LOG = logging.getLogger(__name__)


@application.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    LOG.debug("Request from dialogflow is: %s" % req)
    kwargs = utils.extract_slack_parameters(req)
    kwargs.update(utils.merge_parameters(req))
    if kwargs.get("assignee.login"):
        kwargs['session_id'] = "{}:{}".format(kwargs.get("assignee.login"), kwargs['session_id'])

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
    # NOTE: hard code, mapping between slack id and github account
    # TODO: retrieve these information from database and cache
    # it inside memory
    if kwargs.get("assignee.login") == "U7UJ7Q3RP":
        kwargs["assignee.login"] = "chenzongxiong"

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
    speech = kwargs.pop("speech", None)
    displayText = kwargs.pop("displayText", speech)
    if not speech:
        response = dict(
            source="Lara/lara backend"
        )
    else:
        response = dict(
            speech=json.dumps(speech),
            displayText=json.dumps(displayText),
            source="Lara/lara backend"
        )

    response.update(kwargs)
    LOG.debug(response)
    return response
