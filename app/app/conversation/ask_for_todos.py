from github import Github
from github import Issue
from github import PullRequest

from app.db.api import user_get_by__github_login

import json

def ask_for_todos(user):
    """ Example implementation of the "Ask for todos" feature. It searches issues and pull request in repositories a user 
    has access or contributes to and returns the top three scored issues. If a pull request opened by the user has been
    reviewed, it will also be listed as an extra todo. 

    Args:
        user (models.user.User): Internal user instance

    Returns:
        (str): Lara's answer
    """
    gh = Github(user.github_token)
    ghuser = gh.get_user(user.github_login)
    user_repos = ghuser.get_repos("all")
    issues_and_pulls = []
    pulls_only = []
    
    for repo in user_repos:
        issues_and_pulls += list(repo.get_issues())
        pulls_only += list(repo.get_pulls())
    
    sorted_issues_and_pulls = sorted(issues_and_pulls, key=lambda iop: create_score(iop, ghuser), reverse=True)

    if len(sorted_issues_and_pulls) < 1:
        return "Seems like there is nothing to do."

    response = "I've found the following:"

    top_iops = sorted_issues_and_pulls[:3]

    if len(sorted_issues_and_pulls) > 1:
        response += " These seem the most important to me:\n"
    
    count = 1
    for top_iop in top_iops:
        response += (f"{count}. <{top_iop.html_url}|{top_iop.title}>")

        if top_iop.pull_request == None:
            iop = "Issue"
        else:
            iop = "Pull Request"

        response += " ("
        if top_iop.assignee == ghuser:
            response += (f"{iop} assigned to you")
        elif top_iop.assignee == None:
            response += (f"unassigned {iop}")
        else:
            response += (f"{iop} assigned to {top_iop.assignee.login}")

        response += ")\n"
        count += 1
    

    pull_response = "\nAlso take note that the following Pull Requests have been reviewed: \n"
    count = 0
    for pull in pulls_only:
        reviews = list(pull.get_reviews())
        if len(reviews) > 0:
            count += 1
            pull_response += (f"<{pull.html_url}|{pull.title}>\n")

    if count > 0:
        response += pull_response

    return response


def create_score(issue, user):
    """
    Creates a score for an issue. Its primary criterium is if an issue is assigned to the user or unassigned. Labels are
    use as secondary criterium.

    Args:
        issue (github.Issue): Github issue object
        user (github.NamedUser): Github named user object

    Returns:
        (int): score for issue
    """
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

    if issue.assignee == user:
        score += 1000
    elif issue.assignee == None:
        score += 500

    return score


if __name__ == "__main__":
    user = user_get_by__github_login('testuserlara')
    print(app.conversation.ask_for_todos.ask_for_todos(user))
