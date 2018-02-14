import sqlite3

from flask import Flask, g

from app.authentication.GithubApp import GithubApp

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('config.py')

# Create db if not exists
with sqlite3.connect(application.config['DATABASE']) as conn:
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM user')
        print("Database table user has {} rows".format(len(cursor.fetchall())))
    except sqlite3.OperationalError:
        with open('resources/schema.sql', 'r') as f:
            cursor.execute(f.read())
            conn.commit()


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


# Connect to the Lara GithubApp
with open(application.config['GITHUB_APP_PRIVATE_KEY'], 'r') as f:
    private_key = f.read()
github_app = GithubApp(application.config['GITHUB_APP_ID'], private_key)
# installation = github_app.get_installation(application.config['GITHUB_APP_ID'])


@application.route('/')
def hello_world():
    return 'Hello, World!'


from app import webhook  # noqa
from app.authentication import auth  # noqa
