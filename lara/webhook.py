from lara import app
from clients import GithubClient
from flask import request
from flask import jsonify
import json


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    req = request.get_json(silent=True, force=True)

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
