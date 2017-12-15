from lara import app
from .github_app import GithubApp
from flask_restful import reqparse, Api, Resource
from .clients import GithubClient

# Connecting with the Lara GitHub App
with open(app.config['GITHUB_APP_PRIVATE_KEY'], 'r') as f:
    private_key = f.read()
github_app = GithubApp(app.config['GITHUB_APP_ID'], private_key)

# So far only a single installation is supported
# The encapsulation allows us to use multiple installations on one server in the future though,
# so we could offer the Lara GitHub App as a Service
github_client = GithubClient(github_app, app.config['GITHUB_INSTALLATION_ID'])


class Issue(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title')
        self.parser.add_argument('body')

    def get(self, issue_id):
        return GithubClient.get_repo_issue(issue_id)

    def put(self, issue_id):
        kwargs = self.parser.parse_args()
        resp = GithubClient.update_repo_issue(issue_id, **kwargs)
        return resp, 201


class IssueList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title')
        self.parser.add_argument('body')

    def get(self):
        return GithubClient.list_repo_issues()

    def post(self):
        kwargs = self.parser.parse_args()
        resp = GithubClient.create_repo_issue(**kwargs)
        return resp, 201


@app.route('/')
def hello_world():
    return 'Hello, World!'


api = Api(app)
api.add_resource(Issue, '/issue/<int:issue_id>')
api.add_resource(IssueList, '/issues')
