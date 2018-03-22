import config
from github import Github
from github import Issue
from github import PullRequest

def score_labels(issue):
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
    return score

def score_pull_request(pull):
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
        return score_labels(poi)
    elif isinstance(poi, PullRequest.PullRequest):
        return score_pull_request(poi)
    else:
        return 0


github = Github(config.github_oauth)
test = github.get_organization("LaraTUB").get_repo("test")
user = github.get_user("chenzongxiong")
# user = github.get_user()

all_issues = test.get_issues()
all_pulls_paginated = test.get_pulls()
all_pulls = []
for pull in all_pulls_paginated:
    all_pulls.append(pull)

issues_user = [issue for issue in all_issues if issue.assignee == user]
issues_user = sorted(issues_user, key=score_labels, reverse=True)

issues_and_pulls = issues_user + all_pulls

sorted_issues_and_pulls = sorted(issues_and_pulls, key=create_score, reverse=True)

organization = "airbnb"
#topic_or_lang = raw_input("Please enter a topic or language: ")
topic_or_lang = "Java"

query = "org:" + organization + " topic:" + topic_or_lang
print(query)
search_paginated = github.search_repositories(query)
search_topic = []
for search_page in search_paginated:
    print(search_page)
    search_topic.append(search_page)

print("---")

query = "org:" + organization + " language:" + topic_or_lang
print(query)
search_paginated = github.search_repositories(query)
search_lang = []
for search_page in search_paginated:
    print(search_page)
    search_lang.append(search_page)

print("---")

print("---")
print("diff")
# search = list(set(search_topic + search_lang))
search = search_topic + search_lang
print(search)
print("---")


contribs_for_tag = dict()
for repo in search:
    stats = repo.get_stats_contributors()

    print(repo)
    # print(stats)
    if not stats:
        continue

    for contrib in stats:
        author_login = contrib.author.login
        if author_login in contribs_for_tag.keys():
            contribs_for_tag[author_login] += contrib.total
        else:
            contribs_for_tag[author_login] = contrib.total

for contrib in sorted(contribs_for_tag, key=contribs_for_tag.get, reverse=True):
    print(contrib, contribs_for_tag[contrib])

print(user.login)
print("----------------")
print("----------------")

for pull in all_pulls:
    print(pull.assignee)
    score_pull_request(pull)
    pull_or_issue(pull)

print("****************************************")
print("Issues and Pull Requests prioritized")
print("****************************************")
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
