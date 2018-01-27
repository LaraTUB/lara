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
    msg_fmt = "Organization %(name) not found."


class RepositoryNotProvidedException(LaraException):
    msg_fmt = "Repository not provided."


class RepositoryNotFoundException(LaraException):
    msg_fmt = "Repository %(name) not found."


class IssueIdNotProvidedException(LaraException):
    msg_fmt = "Issue id not provided."


class IssueIdNotFoundException(LaraException):
    msg_fmt = "Issue %(id) not found."


class IssueStateNotProvidedException(LaraException):
    msg_fmt = "Issue state not provided."


class GithubObjectNotFoundExceptino(LaraException):
    msg_fmt = "Github object %(name) not found."


class IssueCommentNotFinishedException(LaraException):
    msg_fmt = "Comments for issue %(id) not finished."
