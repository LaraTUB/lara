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

github = Github("f988fe6e41161df94fc2b50261ce4e8e32393cc1")
test = github.get_organization("LaraTUB").get_repo("test")
user = github.get_user("alexheinrich")
all_issues = test.get_issues()
all_pulls_paginated = test.get_pulls()
all_pulls = []
for pull in all_pulls_paginated:
	all_pulls.append(pull)

issues_user = [issue for issue in all_issues if issue.assignee == user]
issues_user = sorted(issues_user, key=score_labels, reverse=True)

issues_and_pulls = issues_user + all_pulls

sorted_issues_and_pulls = sorted(issues_and_pulls, key=create_score, reverse=True)

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