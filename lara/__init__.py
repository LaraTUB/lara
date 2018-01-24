from flask import Flask, g
from lara.GithubApp import GithubApp

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

# Connect to the Lara GithubApp
with open(app.config['GITHUB_APP_PRIVATE_KEY'], 'r') as f:
    private_key = f.read()
github_app = GithubApp(app.config['GITHUB_APP_ID'], private_key)

import lara.server
# import lara.webhook


