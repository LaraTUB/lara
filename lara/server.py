import random
import string
from http.client import HTTPSConnection
from urllib.parse import parse_qs

from github import Github

from lara import app, get_db
from flask import request, redirect, g


@app.route('/')
def hello_world():
    #installation = github_app.get_installation(app.config['GITHUB_APP_ID'])
    return 'Hello, World!'


@app.route('/auth')
def auth():
    # TODO check parameters
    # TODO factor out authentication tokens
    # TODO created time
    
    db = get_db()

    token = request.args.get('token')
    if token:
        state = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
        db.execute('UPDATE user SET state=? WHERE token=?', (state, token))
        db.commit()
        redirect_url = 'https://github.com/login/oauth/authorize?client_id={}&state={}'.format(app.config['GITHUB_OAUTH_CLIENT_ID'], state)
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
                app.config['GITHUB_OAUTH_CLIENT_ID'],
                app.config['GITHUB_OAUTH_CLIENT_SECRET'],
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

        db.execute('UPDATE user SET github_name=?, github_login=? WHERE state=?', (user.name, user.login, state))
        db.commit()

        return "Successfully connected Slack user id {} with Github user {}".format(rows[0][3], user.login)
    else:
        raise Exception('Bad state', status_code=400)

