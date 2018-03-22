class LaraException(Exception):
    msg_fmt = "An unknown exception occurred."

    def __init__(self, message=None, **kwargs):
        if not message:
            message = self.msg_fmt % kwargs
        super(LaraException, self).__init__(message)


class ServerException(LaraException):
    msg_fmt = "An exception occurs on server %s"


class OrganizationNotProvidedException(LaraException):
    msg_fmt = "Organization not provided."


class OrganizationNotFoundException(LaraException):
    msg_fmt = "Organization %(name)s not found."


class RepositoryNotProvidedException(LaraException):
    msg_fmt = "Repository not provided."


class RepositoryNotFoundException(LaraException):
    msg_fmt = "Repository %(name)s not found."


class IssueIdNotProvidedException(LaraException):
    msg_fmt = "Issue id not provided."


class IssueIdNotFoundException(LaraException):
    msg_fmt = "Issue %(id)s not found."


class IssueStateNotProvidedException(LaraException):
    msg_fmt = "Issue state not provided."


class GithubObjectNotFoundExceptino(LaraException):
    msg_fmt = "Github object %(name)s not found."


class IssueCommentNotFinishedException(LaraException):
    msg_fmt = "Comments for issue %(id)s not finished."


class IssueBodyNotProvidedException(LaraException):
    msg_fmt = "Issue body is not provided."


class IssueTitleNotProvidedException(LaraException):
    msg_fmt = "Issue title is not provided."


class IssueAssigneeNotProvidedException(LaraException):
    msg_fmt = "Issue assignee is not provided."


class IssueLabelNotProvidedException(LaraException):
    msg_fmt = "Issue label is not provided."


class UserNotFound(LaraException):
    msg_fmt = "User %(id)s not found."


class UserNotFoundByGithubLogin(LaraException):
    msg_fmt = "User %(github_login)s not found."


class UserNotFoundBySlackUserId(LaraException):
    msg_fmt = "User %(slack_user_id)s not found."


class UserNotFoundByToken(LaraException)    :
    msg_fmt = "User %(token)s not found."
