from flask_restful import Api, Resource

from app import app
from flask import request
from flask import jsonify
from .clients import GithubClient
import json


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(req)
    resp = process_request(req)
    return jsonify(resp)


def process_request(req):
    speech = "default speech for debug"
    # import pdb; pdb.set_trace()
    req_action = req.get('result').get('action')
    issue_parameters = req.get('result').get('parameters')

    if req_action == 'issue.list':
        try:
            issue_id = int(issue_parameters.get('issue-id'))
        except (ValueError, TypeError):
            issue_id = None

        speech = json.dumps(list_issue(issue_id))

    elif req_action == 'issue.update':
        if issue_parameters.get('issue-action') == 'close':
            issue_id = int(issue_parameters.get('issue-id'))
            speech = json.dumps(close_issue(issue_id))
        elif issue_parameters.get('issue-action') == 'list':
            issue_id = int(issue_parameters.get('issue-id'))
            speech = json.dumps(list_issue(issue_id))
        # if issue_action == 'open':
        #     issue_id = int(req.get('result').get('parameters').get('issue-id'))
        #     speech = json.dumps(open_issue(issue_id))


    return {"speech": speech,
            "displayText": speech,
            "source": "test-apiai"}


def close_issue(issue_id):
    issue = GithubClient.get_repo_issue(issue_id)
    issue.edit(issue.title, issue.body,
               state='closed')

    return issue._rawData


def list_issue(issue_id):
    if not issue_id:
        return [i._rawData for i in GithubClient.list_repo_issues()]

    return GithubClient.get_repo_issue(issue_id)._rawData


class Issue(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title')
        self.parser.add_argument('body')

    def get(self, issue_id):
        return github_client.get_repo_issue(issue_id)

    def put(self, issue_id):
        kwargs = self.parser.parse_args()
        resp = github_client.update_repo_issue(issue_id, **kwargs)
        return resp, 201


class IssueList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title')
        self.parser.add_argument('body')

    def get(self):
        return github_client.list_repo_issues()

    def post(self):
        kwargs = self.parser.parse_args()
        resp = github_client.create_repo_issue(**kwargs)
        return resp, 201


api = Api(app)
api.add_resource(Issue, '/issue/<int:issue_id>')
api.add_resource(IssueList, '/issues')