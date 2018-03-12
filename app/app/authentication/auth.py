import uuid
from http.client import HTTPSConnection
from urllib.parse import parse_qs
from github import Github
from flask import request, redirect
from app import application
from app import log as logging
from app.db import api as dbapi
from app import exceptions

LOG = logging.getLogger(__name__)


@application.route('/auth')
def auth():
    # TODO check parameters
    # TODO factor out authentication tokens
    # TODO created time

    token = request.args.get('token')
    if token:
        state = _get_random_string()
        user = dbapi.user_get_by__token(token=token)
        values = {"state": state}
        user = dbapi.user_update(user.id, values)

        redirect_url = 'https://github.com/login/oauth/authorize?client_id={}&state={}'.format(
            application.config['GITHUB_OAUTH_CLIENT_ID'], state)
        return redirect(redirect_url, code=302)

    code = request.args.get('code')
    if code:
        state = request.args.get('state')
        user = dbapi.user_get_by__state(state=state)

        conn = HTTPSConnection("github.com")
        conn.request(
            method='POST',
            url='/login/oauth/access_token?client_id={}&client_secret={}&code={}&state={}'.format(
                application.config['GITHUB_OAUTH_CLIENT_ID'],
                application.config['GITHUB_OAUTH_CLIENT_SECRET'],
                code,
                state
            ),
            headers={
                "User-Agent": "LaraTUB/lara"
            }
        )
        response = conn.getresponse()
        response_text = response.read().decode('utf-8')
        conn.close()

        access_token = parse_qs(response_text)['access_token'][0]
        gh = Github(access_token)
        gh_user = gh.get_user()

        values = dict(
            github_name=gh_user.name,
            github_login=gh_user.login,
            github_token=access_token
        )
        user = dbapi.user_update(user.id, values)
        return "Successfully connected Slack user id {} with Github user {}".format(
            user.slack_user_id, user.github_login)

    else:
        raise Exception('Bad state', status_code=400)


def build_authentication_message(slack_user_id):
    """Generates and stores a random token and returns a Github authorization URL"""
    try:
        user = dbapi.user_get_by__slack_user_id(slack_user_id)
    except exceptions.UserNotFoundBySlackUserId:
        token = _get_random_string()
        values = dict(
            slack_user_id=slack_user_id,
            token=token
        )
        user = dbapi.user_create(values)

    token = user.token
    return '{}/auth?token={}'.format(application.config['URL'], token)


def _get_random_string():
    return uuid.uuid4().hex
