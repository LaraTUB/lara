from lara import app
from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from clients import GithubClient


@app.route('/')
def hello_world():
    return 'Hello, World!'


api = Api(app)

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


api.add_resource(Issue, '/issue/<int:issue_id>')
api.add_resource(IssueList, '/issues')
