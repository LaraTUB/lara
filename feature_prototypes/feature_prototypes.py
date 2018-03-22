import config
from github import Github
from github import Issue
from github import PullRequest


def score():
    gh = get_gh()
    test = gh.get_organization("LaraTUB").get_repo("test")
    user = gh.get_user()

    # owned + forked + private with access + organization repos
    all_issues = list(test.get_issues())
    all_pull_requestst = list(test.get_pulls())
    # user_pull_requestst = [issue for issue in all_issues if issue.assignee and issue.assignee.login == user.login]

    issues_and_pulls = all_issues + all_pull_requestst
    sorted_issues_and_pulls = sorted(issues_and_pulls, key=create_score, reverse=True)
    return sorted_issues_and_pulls


def help():
    gh = get_gh()

    # Hardcode
    organization = "airbnb"
    # topic_or_lang = raw_input("Please enter a topic or language: ")
    topic_or_lang = "Java"

    query = "org:" + organization + " topic:" + topic_or_lang
    print(query)
    search_paginated = gh.search_repositories(query)
    search_topic = []
    for search_page in search_paginated:
        print(search_page)
        search_topic.append(search_page)
    print("---")
    query = "org:" + organization + " language:" + topic_or_lang
    print(query)
    search_paginated = gh.search_repositories(query)
    search_lang = []
    for search_page in search_paginated:
        print(search_page)
        search_lang.append(search_page)
    print("---")

    print("---")
    print("diff")
    search = list(set(search_topic + search_lang))  # TODO compare
    print(search)
    print("---")

    contribs_for_tag = dict()
    for repo in search:
        stats = repo.get_stats_contributors()
        print(repo)
        # print(stats)
        for contrib in stats:
            author_login = contrib.author.login
            if author_login in contribs_for_tag.keys():
                contribs_for_tag[author_login] += contrib.total
            else:
                contribs_for_tag[author_login] = contrib.total

    for contrib in sorted(contribs_for_tag, key=contribs_for_tag.get, reverse=True):
        print
        contrib, contribs_for_tag[contrib]

    print(user.login)
    print("----------------")
    print("----------------")

    for pull in all_pulls:
        print(pull.assignee)
        score_pull_request(pull)
        pull_or_issue(pull)

    print("Issues and Pull Requests prioritized")
    print("----------------")
    print("----------------")

    for poi in sorted_issues_and_pulls:
        print(poi)
        if isinstance(poi, Issue.Issue):
            labels = poi.labels
            print(poi.assignee)
        else:
            print(poi.assignee)

        score = create_score(poi)
        print(score)
        print("----------------")


def get_gh():
    github = Github(config.github_oauth)
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


def score_pull_request(pull):
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


def pull_or_issue(poi):
    if isinstance(poi, Issue.Issue):
        print("this is a issue")
    elif isinstance(poi, PullRequest.PullRequest):
        print("this is a pull req")
    else:
        print("this is something else")


def create_score(poi):
    if isinstance(poi, Issue.Issue):
        return score_issues(poi)
    elif isinstance(poi, PullRequest.PullRequest):
        return score_pull_request(poi)
    else:
        return 0


if __name__ == "__main__":
    score()
