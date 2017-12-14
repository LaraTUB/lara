from lara import app
from github import Github

git_handler = Github(app.config['GITHUB_USERNAME'],
                     app.config['GITHUB_PASSWORD'])

organization = git_handler.get_organization(app.config.get('ORGANIZATION', 'LaraTUB'))
repo = organization.get_repo(app.config.get('REPO', 'lara'))


class GithubClient(object):

    @staticmethod
    def get_user():
        return git_handler.get_user()

    @staticmethod
    def get_organization():
        return organization

    @staticmethod
    def list_org_issues():
        return [issue for issue in organization.get_issues()]

    @staticmethod
    def list_repo_issues():
        return [issue for issue in repo.get_issues()]

    @staticmethod
    def create_repo_issue(title, body):
        return repo.create_issue(title, body)

    @staticmethod
    def update_repo_issue(issue_id, title, body, **kwargs):
        issue = repo.get_issue(issue_id)
        issue.edit(title, body, **kwargs)
        return repo.get_issue(issue_id)

    @staticmethod
    def get_repo_issue(issue_id):
        issue = repo.get_issue(issue_id)
        return issue
