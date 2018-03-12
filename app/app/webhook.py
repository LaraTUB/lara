import json

from flask import jsonify
from flask import request

from app import application, get_db
from app import exceptions
from app import log as logging
from app import trigger
from app import utils
from app.authentication import auth
from app.objects import get_git_object
from app.db import api as dbapi


LOG = logging.getLogger(__name__)


@application.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    LOG.debug("Request from dialogflow is: %s" % req)

    # TODO Refactor
    kwargs = utils.extract_slack_parameters(req)
    kwargs.update(utils.merge_parameters(req))

    # Why do we need to do this?
    if kwargs.get("assignee.login"):
        kwargs['session_id'] = "{}:{}".format(kwargs.get("assignee.login"), kwargs['session_id'])

    # Authenticate
    if "originalRequest" not in req:  # Only for debugging
        github_login = "chenzongxiong"
    else:
        original_request = req["originalRequest"]
        if original_request["source"] != "slack":
            LOG.error("Only Slack supported")
            raise exceptions.LaraException()
        slack_user_id = original_request["data"]["event"]["user"]

        try:
            user = dbapi.user_get_by__slack_user_id(slack_user_id)
        except exceptions.UserNotFoundBySlackUserId:
            LOG.debug("Slack User unknown, asking for authentication with token xxx")
            return respond(speech="Please authenticate with Github:\n" + auth.build_authentication_message(slack_user_id))
        else:
            if not user.github_login:
                LOG.debug("Gihub Login unknown, asking for authentication with token xxx")
                return respond(speech="Please authenticate with Github:\n" + auth.build_authentication_message(slack_user_id))


        github_login = user.github_login
        LOG.debug("Request by " + kwargs["assignee.login"])

    kwargs["assignee.login"] = github_login
    try:
        if req["result"]["action"]:
            name, action = req["result"]["action"].split("_")
        else:
            name, action = kwargs.pop("action", "").split("_")
        LOG.debug("Request for github object *%s*, play *%s* action" % (name, action))
        LOG.debug("Request parameters are %s" % kwargs)
        # NOTE: each user has a git object handler.
        handler = getattr(get_git_object("{}:{}".format(github_login, name)),
                          action)
    except ValueError:
        # TODO implement handler for more general commands like "ListAllIssues"
        action = req["result"]["action"]
        def handler():
            return "Basic result"

    try:
        # TODO way to pass
        results = handler(**kwargs)
    except exceptions.RepositoryNotProvidedException:
        LOG.debug("Trigger Repository Missing Event.")
        followup_event = trigger.repository_missing_event(action="{}_{}".format(name, action), **kwargs)
        return respond(**followup_event)
    except exceptions.IssueCommentNotFinishedException:
        LOG.debug("Trigger Issue Comemnt Not Finished Event.")
        followup_event = trigger.issue_comment_not_finished_event(action="{}_{}".format(name, action), **kwargs)
        return respond(**followup_event)
    except exceptions.IssueIdNotProvidedException:
        LOG.error("Issue id not provided.")
    except:
        raise exceptions.LaraException()

    return respond(speech=json.dumps(results))


def respond(**kwargs):
    """Responds to dialogflow"""
    speech = kwargs.pop("speech", None)
    displayText = kwargs.pop("displayText", speech)
    if not speech:
        response = dict(
            source="Lara/lara backend"
        )
    else:
        # "speech" is the spoken version of the response, "displayText" is the visual version
        response = dict(
            speech=speech,
            displayText=displayText,
            source="Lara/lara backend"
        )

    response.update(kwargs)
    LOG.debug(response)
    return jsonify(response)
