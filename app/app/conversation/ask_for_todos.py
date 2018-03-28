from github import Github
from github import Issue
from github import PullRequest

import json

def ask_for_todos(username, password):
    gh = get_gh(username, password)
    test = gh.get_organization("LaraTUB").get_repo("test")
    # TODO: this seems to return a generic user, which can be used to query all contributed/visible repos... find out if this is actually what is going on.
    user = gh.get_user()
    user_repos = user.get_repos()
    all_issues = []
    all_pull_requests = []
    
    for repo in user_repos:
        all_issues += list(repo.get_issues())
        all_pull_requests += list(repo.get_pulls())
    
    all_issues = [
        issue
        for issue in all_issues 
        if (issue.assignee and issue.assignee.login == username) or (issue.user and username)
    ]

    issues_and_pulls = all_issues + all_pull_requests
    sorted_issues_and_pulls = sorted(issues_and_pulls, key=lambda iop: create_score(iop, user), reverse=True)
    #print_iop_with_score(sorted_issues_and_pulls, user)
    
    if len(sorted_issues_and_pulls) < 1:
        return "Seems like you have nothing to do."

    response = "I've found "

    if len(all_issues) == 1:
        response += "one Issue"
    elif len(all_issues) > 1:
        response += (f"{len(all_issues)} Issues")

    if len(all_issues) >= 1 and len(all_pull_requests) >= 1:
        response += " and "

    if len(all_pull_requests) == 1:
        response += "one Pull Request"
    elif len(all_pull_requests) > 1:
        response += (f"{len(all_pull_requests)} Pull Requests")

    top_issue = sorted_issues_and_pulls[:1][0]
    response += (f". This issue seems the most important to me: {top_issue.title}")

    return response


def score(username, password):

    return sorted_issues_and_pulls


def get_gh(username, password):
    github = Github(username, password)
    return github


def print_iop_with_score(iops, user):
    print("----------")
    print("Listing all issues and pull requests with score:")
    
    for iop in iops:
        print("---")
        print(iop)
        print(create_score(iop, user))

    print("----------")


def score_issues(issue, user):
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
    issue
    # TODO created by

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


def create_score(iop, user):
    if isinstance(iop, Issue.Issue):
        return score_issues(iop, user)
    elif isinstance(iop, PullRequest.PullRequest):
        return score_pull_request(iop, user)
    else:
        return 0


if __name__ == "__main__":
    print(ask_for_todos())
