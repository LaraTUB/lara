import sqlite3

from flask import Flask, g, render_template
from github import Github

from app.authentication.GithubApp import GithubApp

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('default.py', silent=True)
application.config.from_pyfile('config.py')

# Create db if not exists
# with sqlite3.connect(application.config['DATABASE']) as conn:
#     cursor = conn.cursor()
#     try:
#         cursor.execute('SELECT * FROM user')
#         print("Database table user has {} rows".format(len(cursor.fetchall())))
#     except sqlite3.OperationalError:
#         with open('resources/schema.sql', 'r') as f:
#             cursor.execute(f.read())
#             conn.commit()


# # Database connection
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(application.config['DATABASE'])
#     return db


# def get_gh(github_login):
#     db = get_db()
#     github_token = db.execute('SELECT github_token FROM user WHERE github_login=?', (github_login,)).fetchall()[0][0]
#     return Github(github_token)


# @application.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


# Connect to the Lara GithubApp
#with open(application.config['GITHUB_APP_PRIVATE_KEY'], 'r') as f:
#    private_key = f.read()
#    github_app = GithubApp(application.config['GITHUB_APP_ID'], private_key)
#    installation = github_app.get_installation(112151)
#    pass


from app.db import api as dbapi    # noqa
from app import webhook  # noqa
from app.authentication import auth  # noqa


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
