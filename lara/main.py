import sqlite3

from flask import Flask, g
from lara.GithubApp import GithubApp

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

# Connect to the Lara GithubApp
with open(app.config['GITHUB_APP_PRIVATE_KEY'], 'r') as f:
    private_key = f.read()
github_app = GithubApp(app.config['GITHUB_APP_ID'], private_key)

# Database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

import lara.server
# import lara.webhook


if __name__ == '__main__':
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)