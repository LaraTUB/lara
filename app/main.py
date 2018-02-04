import sqlite3

from flask import Flask, g
from app.GithubApp import GithubApp

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('config.py')

# Connect to the Lara GithubApp
with open(application.config['GITHUB_APP_PRIVATE_KEY'], 'r') as f:
    private_key = f.read()
github_app = GithubApp(application.config['GITHUB_APP_ID'], private_key)

# Database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(application.config['DATABASE'])
    return db

@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

import app.server
# import app.webhook


if __name__ == '__main__':
    # Only for debugging while developing
    application.run(host='0.0.0.0', debug=True, port=80)