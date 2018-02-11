from flask import Flask

application = Flask(__name__, instance_relative_config=True)

application.config.from_object('config.default')
application.config.from_pyfile('config.py')

try:
    application.config.from_envvar('APP_CONFIG_FILE')
except RuntimeError:
    pass


from lara import webhook
from lara.app import auth
