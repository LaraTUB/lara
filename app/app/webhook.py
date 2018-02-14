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
        db = get_db()
        row = db.execute('SELECT github_login FROM user WHERE slack_user_id=?', (slack_user_id,)).fetchall()
        if len(row) == 1:
            github_login = row[0][0]
            LOG.debug("Request by " + kwargs["assignee.login"])
        elif len(row) == 0:
            LOG.debug("User unknown, asking for authentication with token xxx")
            return respond("Please authenticate with Github:\n" + auth.build_authentication_message(slack_user_id))
        else:
            LOG.error("Weird database state!")
            raise exceptions.LaraException()

    kwargs["assignee.login"] = github_login

    if req["result"]["action"]:
        try:
            name, action = req["result"]["action"].split("_")
            LOG.debug("Request for github object *%s*, play *%s* action" % (name, action))
            LOG.debug("Request parameters are %s" % kwargs)
            handler = getattr(get_git_object(name), action)
        except ValueError:
            # TODO implement
            action = req["result"]["action"]
            def handler():
                return "Basic result"
    # else:
    #     name, action = kwargs.pop("action", "").split("_")

    try:
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

    return respond(json.dumps(results))


def respond(response):
    """Responds to dialogflow"""
    if not response:
        response = dict(
            source="Lara/lara backend"
        )
    else:
        # "speech" is the spoken version of the response, "displayText" is the visual version
        response = dict(
            speech=response,
            displayText=response,
            source="Lara/lara backend"
        )

    LOG.debug(response)
    return jsonify(response)
