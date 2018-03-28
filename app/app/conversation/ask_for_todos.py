from github import Github
from github import Issue
from github import PullRequest

import json

def ask_for_todos(username, password):
    issue_list = score(username, password)
    response = ""
    
    if len(issue_list) < 1:
        return "Seems like you have nothing to do."

    top_issue = issue_list[:1][0]
    response = (f"I've found {len(issue_list)} issues. This issue seems the most important to me: {top_issue.title}")

    return response


def score(username, password):
    gh = get_gh(username, password)
    test = gh.get_organization("LaraTUB").get_repo("test")
    user = gh.get_user()

    # owned + forked + private with access + organization repos
    all_issues = list(test.get_issues())
    all_pull_requests = list(test.get_pulls())
    # user_pull_requests = [issue for issue in all_issues if issue.assignee and issue.assignee.login == user.login]

    issues_and_pulls = all_issues + all_pull_requests
    sorted_issues_and_pulls = sorted(issues_and_pulls, key=lambda iop: create_score(iop, user), reverse=True)
    return sorted_issues_and_pulls

def get_gh(username, password):
    github = Github(username, password)
    return github


def score_issues(issue):
    labels = issue.labels
    score = 0
    for label in labels:
        if "critical" == label.name:
            score += 100
        elif "high" == label.name:
            score += 70
        elif "low" == label.name:
            score += 10
        elif "bug" == label.name:
            score += 40
        elif "help wanted" == label.name:
            score += 50

    # TODO assigned to
    # created by

    return score


def score_pull_request(pull, user):
    """Returns a score on how important a certain pull request is"""

    # TODO add pull requests issued by the user (that have been reviewed)
    # TODO also show pull requests not assigned/created by the user

    if pull.assignee == user:
        score = 50
    elif pull.assignee == None:
        score = 30
    else:
        score = 0
    return score


def pull_or_issue(iop):
    if isinstance(iop, Issue.Issue):
        print("this is a issue")
    elif isinstance(iop, PullRequest.PullRequest):
        print("this is a pull req")
    else:
        print("this is something else")


def create_score(iop, user):
    if isinstance(iop, Issue.Issue):
        return score_issues(iop)
    elif isinstance(iop, PullRequest.PullRequest):
        return score_pull_request(iop, user)
    else:
        return 0


if __name__ == "__main__":
    print(ask_for_todos())
