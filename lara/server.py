import random
import string
from http.client import HTTPSConnection
from urllib.parse import parse_qs
from lara import app
from flask import request, redirect, g
from lara import github_app

@app.route('/')
def hello_world():
    installation = github_app.get_installation(app.config['GITHUB_APP_ID'])
    installation
    return 'Hello, World!'


@app.route('/login/callback')
def login_callback():
    #if g.get('states') is None:
    #    g.states = []
    code = request.args.get('code')
    if code is None:
        random_state = 'aaa' # ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        #g.states.append(random_state)
        redirect_url = 'https://github.com/login/oauth/authorize?client_id={}&state={}'.format(app.config['GITHUB_OAUTH_CLIENT_ID'], random_state)
        return redirect(redirect_url, code=302)
    state = request.args.get('state')
    if state in ['aaa']:
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
        return parse_qs(response_text)
    else:
        raise Exception('Bad state', status_code=400)

