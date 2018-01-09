from lara import app
from clients import GithubClient
from flask import request
from flask import jsonify
import json


user = GithubClient.get_user()
__login__ = user.login

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    req = request.get_json(silent=True, force=True)

    resp = process_request(req)
    return jsonify(resp)


def process_request(req):
    speech = "default speech for debug"
    display_text = None
    # import pdb; pdb.set_trace()
    print(req)
    req_action = req.get('result').get('action')
    print(req_action)
    issue_parameters = req.get('result').get('parameters')
    print(issue_parameters)

    if req_action == 'issue':
        speech, display_text = stat_issue()

    if req_action == 'issue.list':
        try:
            issue_id = int(issue_parameters.get('issue-id'))
        except (ValueError, TypeError):
            issue_id = None
        if issue_parameters.get('issue-parameters') == 'true':
            issue_id = -1

        speech, display_text = list_issue(issue_id)

    if req_action == 'issue.update':
        try:
            issue_id = int(issue_parameters.get('issue-id'))
        except (ValueError, TypeError):
            issue_id = None

        speech, display_text = close_issue(issue_id)
    if req_action == 'issue.create':
        title = issue_parameters.get('issue-title')
        body = issue_parameters.get('issue-body')
        assignee = issue_parameters.get('issue-assignee')
        speech, display_text = create_issue(title, body, assignee)

    return build_response(speech, display_text)


def build_response(speech, display_text=None):
    if not display_text:
        display_text = speech

    return {"speech": json.dumps(speech),
            "displayText": json.dumps(display_text),
            "source": "chatbot-backend"}


"""
Extract meaningful issue content from raw data
Parameters
----------
issue: `object`, an issue instance

Return
----------
d: `dict`, a dictionary contain the value we are interested
"""
def _extract(issue):
    raw_data = issue._rawData
    KEYS = ['title', 'body', 'assignee', 'created_at', 'closed_at',
            'number', 'assignees']
    d = {}
    for key, value in raw_data.iteritems():
        if key not in KEYS:
            continue

        if key == "assignee" and value is not None:
            d[key] = value['login']
        if key == 'assignees':
            d[key] = [assignee['login'] for assignee in value]
        d[key] = value

    return d


"""
List the status of issues
Parameters
----------

Returns
----------
speech: the context play via audio
display_text: the context diplay on the screen
"""
def stat_issue():
    display_text = [_extract(issue) for issue in GithubClient.list_repo_issues()]
    count = len(display_text)
    print display_text
    return "There are {} issues are for you. Can I list them on the screen".format(count), display_text

def close_issue(issue_id):
    # import pdb; pdb.set_trace()
    issue = GithubClient.get_repo_issue(issue_id)
    issue.edit(issue.title, issue.body,
               state='closed')

    print(issue._rawData)
    return "Close issue " + issue.title, _extract(issue)


def list_issue(issue_id):
    if not issue_id:
        return "Not Found issue, sorry", None
    if issue_id == -1:
        # list all issues
        _, display_text = stat_issue()
        return display_text, display_text

    issue = GithubClient.get_repo_issue(issue_id)
    user = GithubClient.get_user()
    print user.login
    print issue._rawData
    return "List issue " + issue.title, _extract(issue)


def create_issue(title, body, assignee=None):
    issue = GithubClient.create_repo_issue(title, body)
    print issue._rawData
    return "Create sucessfully!", _extract(issue)
