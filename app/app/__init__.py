from flask import Flask, render_template
from github import Github

from app.authentication.GithubApp import GithubApp

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('default.py', silent=True)
application.config.from_pyfile('config.py')

from app.db import api as dbapi    # noqa
from app import webhook  # noqa
from app.authentication import auth  # noqa
from app.db import events as dbevents # noqa


@application.route('/')
def hello_world():
    users = dbapi.user_get_all()
    user_list = []
    for user in users:
        if not user.github_token:
            continue
        gh_user = Github(user.github_token).get_user()
        values = dict(name=gh_user.name,
                      avatar=gh_user.avatar_url,
                      url=gh_user.html_url,
                      github=user.github_login,
                      slack=user.slack_user_id)
        user_list.append(values)

    return render_template('index.html', users=user_list)
