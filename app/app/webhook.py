import json

from flask import jsonify
from flask import request

from app import application, get_db, get_gh
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
    LOG.debug("Request from dialogflow: %s" % req)

    # Authenticate
    if "originalRequest" not in req or req["originalRequest"]["source"] != "slack":
        return respond(speech="Only requests via Slack supported")

    original_request = req["originalRequest"]

    kwargs = {
        "assignee.login": original_request["data"]["event"]["user"],
        "team_id": original_request["data"]["team_id"],
        "request_source": "slack"
    }

    def merge_parameters(req):
        kwargs = req["result"]["parameters"]
        parameters = dict()
        for key, value in kwargs.items():
            if key.startswith("last_"):
                key = key.split("_")[-1]
                if not parameters.get(key):
                    parameters[key] = value
            else:
                parameters[key] = value

        parameters['session_id'] = req['sessionId']
        return parameters

    kwargs.update(utils.merge_parameters(req))



    # Why do we need to do this?
    if kwargs.get("assignee.login"):
        kwargs['session_id'] = "{}:{}".format(kwargs.get("assignee.login"), kwargs['session_id'])

######################################################

    slack_user_id = original_request["data"]["event"]["user"]
    db = get_db()
    row = db.execute('SELECT github_login FROM user WHERE slack_user_id=?', (slack_user_id,)).fetchall()
    if len(row) == 1:
        github_login = row[0][0]
        LOG.debug("Request by " + github_login)
    elif len(row) == 0:
        LOG.debug("User unknown, asking for authentication with token xxx")
        return respond(speech="Please authenticate with Github:\n" + auth.build_authentication_message(slack_user_id))
    else:
        LOG.error("Weird database state!")
        raise exceptions.LaraException()

    # NEW
    action = req["result"]["action"]
    if action == 'hello':
        gh = get_gh(github_login)
        first_name = gh.get_user().name.split(' ')[0]
        return respond(speech="Hi " + first_name)

    # OLD
    kwargs["assignee.login"] = github_login
    try:
        if action:
            name, action = action.split("_")
        else:
            name, action = kwargs.pop("action", "").split("_")
        LOG.debug("Request for github object *%s*, play *%s* action" % (name, action))
        LOG.debug("Request parameters are %s" % kwargs)
        handler = getattr(get_git_object(name), action)
    except ValueError:
        LOG.error("Unknown action")
        return respond(speech="Unknown action")

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