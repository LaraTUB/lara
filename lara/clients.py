from github import Github


class GithubClient(object):

    def __init__(self, github_app, installation_id):
        auth = github_app.get_access_token(installation_id)
        self.gh = Github(auth.token)
        self.organization = self.gh.get_organization()
        # Repository is hardocded until we implement multi repo support
        self.repo = self.organization.get_repo('test')

    def get_user(self):
        return self.gh.get_user()

    def get_organization(self):
        return self.organization

    def list_org_issues(self):
        return [issue for issue in self.organization.get_issues()]

    def list_repo_issues(self):
        return [issue for issue in self.repo.get_issues()]

    def create_repo_issue(self, title, body):
        return self.repo.create_issue(title, body)

    def update_repo_issue(self, issue_id, title, body, **kwargs):
        issue = self.repo.get_issue(issue_id)
        issue.edit(title, body, **kwargs)
        return self.repo.get_issue(issue_id)

    def get_repo_issue(self, issue_id):
        issue = self.repo.get_issue(issue_id)
        return issue
