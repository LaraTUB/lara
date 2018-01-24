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


