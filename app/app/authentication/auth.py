import uuid
from http.client import HTTPSConnection
from urllib.parse import parse_qs
from github import Github
from flask import request, redirect
from app import application, get_db
from app import log as logging

LOG = logging.getLogger(__name__)


@application.route('/auth')
def auth():
    # TODO check parameters
    # TODO factor out authentication tokens
    # TODO created time

    db = get_db()

    token = request.args.get('token')
    if token:
        state = _get_random_string()
        db.execute('UPDATE user SET state=? WHERE token=?', (state, token))
        db.commit()
        redirect_url = 'https://github.com/login/oauth/authorize?client_id={}&state={}'.format(
            application.config['GITHUB_OAUTH_CLIENT_ID'], state)
        return redirect(redirect_url, code=302)

    code = request.args.get('code')
    if code:
        state = request.args.get('state')
        rows = db.execute('SELECT * FROM user WHERE state=?', (state,)).fetchall()
        if len(rows) != 1:
            raise Exception

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
        user = gh.get_user()

        db.execute('UPDATE user SET github_name=?, github_login=?, github_token=? WHERE state=?',
                   (user.name, user.login, access_token, state))
        db.commit()

        return "Successfully connected Slack user id {} with Github user {}".format(rows[0][3], user.login)
    else:
        raise Exception('Bad state', status_code=400)


def build_authentication_message(slack_user_id):
    """Generates and stores a random token and returns a Github authorization URL"""
    token = _get_random_string()
    db = get_db()
    db.execute('INSERT INTO user (slack_user_id, token) VALUES (?, ?)', (slack_user_id, token))
    db.commit()
    return '{}/auth?token={}'.format(application.config['URL'], token)


def _get_random_string():
    return uuid.uuid4().hex
