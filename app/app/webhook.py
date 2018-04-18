import json

from github import Github
from flask import jsonify
from flask import request

from app import application
from app import exceptions
from app import log as logging
from app import trigger
from app import utils
from app import manager
from app.authentication import auth
from app.conversation.ask_for_help import ask_for_help
from app.conversation.ask_for_todos import ask_for_todos
from app.db import api as dbapi


LOG = logging.getLogger(__name__)


@application.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Endpoint for the dialogflow fulfillment webhook"""

    req = request.get_json(silent=True, force=True)
    LOG.debug("Request from dialogflow: %s" % req)

    if "originalRequest" not in req or req["originalRequest"]["source"] != "slack":
        return respond(speech="Only requests via Slack supported")

    # Authenticate
    slack_user_id = req["originalRequest"]["data"]["event"]["user"]
    try:
        user = dbapi.user_get_by__slack_user_id(slack_user_id)
    except exceptions.UserNotFoundBySlackUserId:
        LOG.debug("Slack User unknown, asking for authentication with token xxx")
        return respond(speech="Hi! Please authenticate with Github:\n" + auth.build_authentication_message(slack_user_id))

    if not user.github_token:
        LOG.debug("Gihub Login unknown, asking for authentication with token xxx")
        return respond(speech="Hi! Please authenticate with Github:\n" + auth.build_authentication_message(slack_user_id))

    # Handle actions
    action = req["result"]["action"]
    print(action)
    if action == "hello":
        return respond(speech="Hi " + user.github_login)

    if action == 'find-colleagues':
        colleagues = manager.find_colleagues_matching_skills(user.github_login)
        if len(colleagues) == 0:
            return respond(speech="Sorry. Everyone is struggling for coming deadline! No one could support you.")

        text = ""
        for github_token, issue_count in colleagues:
            gh = Github(github_token)
            user = gh.get_user()
            if issue_count != 0:
                text += "<{}|{}> has only {} open issues. ".format(user.html_url, user.login, issue_count)
            else:
                text += "<{}|{}> finished all issues. ".format(user.html_url, user.login)

        suffix = "them" if len(colleagues) > 1 else "him/her"
        text += "You can ask {} for help.".format(suffix)

        return respond(speech="Found Colleagues. " + text)

    try:
        parameters = req["result"]["parameters"]
        if action == "ask_for_help":
            if parameters["organization"]:
                result = ask_for_help(user, parameters["topic"], parameters["organization"])
            else:
                result = ask_for_help(user, parameters["topic"])
            return respond(speech=result)

        if action == "ask_for_todos":
            return respond(speech=ask_for_todos(user))

        # Place other actions here

    except Exception as e:
        LOG.error("Unexpected exception: " + e)
        return respond(speech="I am sorry, an unknown error occurred...")


    # try:
    #     # TODO way to pass
    #     results = handler(**kwargs)
    # except exceptions.RepositoryNotProvidedException:
    #     LOG.debug("Trigger Repository Missing Event.")
    #     followup_event = trigger.repository_missing_event(action="{}_{}".format(name, action), **kwargs)
    #     return respond(**followup_event)
    # except exceptions.IssueCommentNotFinishedException:
    #     LOG.debug("Trigger Issue Comemnt Not Finished Event.")
    #     followup_event = trigger.issue_comment_not_finished_event(action="{}_{}".format(name, action), **kwargs)
    #     return respond(**followup_event)
    # except exceptions.IssueIdNotProvidedException:
    #     LOG.error("Issue id not provided.")
    # except:
    #     raise exceptions.LaraException()

    return respond(speech="Sorry, I did not understand what you want")


def respond(**kwargs):
    """Responds to dialogflow

    "speech" is the spoken version of the response, "displayText" is the visual version
    """
    speech = kwargs.pop("speech", None)
    displayText = kwargs.pop("displayText", speech)
    if not speech:
        response = dict(
            source="Lara/lara backend"
        )
    else:
        response = dict(
            speech=speech,
            displayText=displayText,
            source="Lara/lara backend"
        )

    response.update(kwargs)
    LOG.debug(response)
    return jsonify(response)
