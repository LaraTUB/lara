from github import Github
from github.GithubException import UnknownObjectException
from lara import app
from lara.cache import get_cache_handler
import trigger
import log as logging
import exceptions
import utils
from utils import serializer_fields, filter_fields, get_desired_parameters


git_handler = Github(app.config['GITHUB_USERNAME'],
                     app.config['GITHUB_PASSWORD'])

LOG = logging.getLogger(__name__)

GIT_HANDLER = None
ORGANIZATION = None

def _get_github_handler_lazily():
    global GIT_HANDLER

    # TODO: use token instead of private login information
    if not GIT_HANDLER:
        GIT_HANDLER = Github(app.config['GITHUB_USERNAME'],
                             app.config['GITHUB_PASSWORD'])

    return GIT_HANDLER


def _get_organization_lazily():
    global ORGANIZATION

    # NOTE: oragnization name should be provided by the incoming request
    if ORGANIZATION is None:
        ORGANIZATION = _get_github_handler_lazily().get_organization(app.config.get('ORGANIZATION', 'LaraTUB'))

    return ORGANIZATION


class Repository():

    _search_fields = ("fork", "language", "repo", "user", "stars", "topic")

    @classmethod
    @serializer_fields("name", "description", "has_issues", "full_name")
    def list(cls, **kwargs):
        name = kwargs.get("name")
        if not name:
            return _get_organization_lazily().get_repos()
        try:
            return _get_organization_lazily().get_repo(name)
        # except github_exceptions.UnknownObjectException():
        except UnknownObjectException:
            raise exceptions.RepositoryNotFoundException(name)


    @classmethod
    def search(cls, **kwargs):
        query = kwargs.pop("query", "")
        qualifiers = dict()
        for key, value in kwargs.items():
            if key in cls._search_fields and value:
                qualifiers[key] = value

        return _get_github_handler_lazily().search_repositories(query, **qualifiers)


    def __repr__(self):
        return "Repository"



class Issue():
    repository = None
    last_repository_name = None
    # TODO: place this comment content in buffer pool,
    # for example, use `sessionId`, `user-identifier` or `token`
    # to track different users
    body = ""
    cache = get_cache_handler()
    _search_fields = ("in", "author", "assignee", "mentions",
                      "involves", "team", "state", "labels",
                      "language", "is", "merged", "closed",
                      "status", "comments",
                      "project")
    @classmethod
    def _get_repository(cls, **kwargs):
        # TODO: set timeout for the repository instance

        if cls.repository is not None and \
           not kwargs.get("repository", None):
            return cls.repository

        name = kwargs.pop("repository", None)

        if not name:
            raise exceptions.RepositoryNotProvidedException()

        # TODO: handle case-sensitive, assuming all the input repository name is lower-case.
        # Here, sanity using the newly provided repository name, although
        # the repository maybe doesn't change
        cls.repository = _get_organization_lazily().get_repo(name)
        cls.last_repository_name = name
        return cls.repository


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @filter_fields("id", "assignee.login")
    @get_desired_parameters("id", "repository", "state", "since", "labels")
    def list(cls, **kwargs):
        # import ipdb; ipdb.set_trace()
        cls._get_repository(**kwargs)
        kwargs.pop("repository", "")
        id = kwargs.pop("id", None)
        state = kwargs.pop("state", "all")
        since = kwargs.pop("since", None)
        if state:
            kwargs['state'] = state
        if since:
            kwargs['since'] = utils.make_datetime(since.split("/")[0])

        if not id:
            return cls.repository.get_issues(**kwargs)
        try:
            return cls.repository.get_issue(id)
        except UnknownObjectException:
            raise exceptions.IssueIdNotFoundException(id)


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("id", "repository")
    def close(cls, **kwargs):
        cls._get_repository(**kwargs)
        try:
            id = kwargs["id"]
        except KeyError:
            raise exceptions.IssueIdNotProvidedException()
        try:
            issue = cls.repository.get_issue(id)
        except UnknownObjectException:
        # except github_exceptions.UnknownObjectException():
            raise exceptions.IssueIdNotFoundException(id)

        return issue.edit(state="closed")


    # TODO: only pass desired parameters to remote
    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("repository")
    def create(cls, **kwargs):
        cls._get_repository(**kwargs)
        issue = cls.repository.create(**kwargs)
        return issue


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("id", "repository", "body", "finished")
    def comment(cls, **kwargs):
        cls._get_repository(**kwargs)
        try:
            id = kwargs["id"]
        except KeyError:
            raise exceptions.IssueIdNotProvidedException()

        # TODO: handle incoming requests contains comment body
        body = kwargs.pop("body", "")
        if not cls.cache.get("key"):
            cls.cache.set("key", body, trigger.issue_comment_timeout_event)
        else:
            _body = cls.cache.get("key") + "\n" + body
            cls.cache.set("key", _body, trigger.issue_comment_timeout_event)

        LOG.debug("Inside cache, the comment is: %s." % cls.cache.get("key"))
        if not kwargs.get("finished") or kwargs["finished"].upper() != "YES":
            raise exceptions.IssueCommentNotFinishedException(id)


        if not cls.cache.get("key"):
            # NOTE: keep salient
            LOG.debug("Doesn't receive any comments.")
            return

        try:
            issue = cls.repository.get_issue(id)
        except UnknownObjectException:
        # except github_exceptions.UnknownObjectException():
            raise exceptions.IssueIdNotFoundException(id)

        # TODO: check whether the issue is open?
        issue_comment = issue.create_comment(body=cls.cache.get("key"))
        # NOTE: this value is comsumed, remove it from cache
        cls.cache.delete("key")

        return issue_comment

    @classmethod
    def update(cls, **kwargs):
        # TODO: may be deprecated
        cls._get_repository(**kwargs)
        try:
            id = kwargs["id"]
            kwargs.pop("id")
        except KeyError:
            raise exceptions.IssueIdNotProvidedException()

        issue = cls.repository.get_issue(id)
        issue.edit(**kwargs)
        return issue


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    def search(cls, **kwargs):
        # TODO: before pass values into `search`
        # we should do check whether those parameters are valid or not

        query = kwargs.pop("query", "")
        qualifiers = dict()
        for key, value in kwargs.items():
            if key in cls._search_fields and value:
                qualifiers[key] = value
        query = "test"
        # qualifiers["project"] = "LaraTUB"
        # qualifiers["repo"] = "test"
        # qualifiers["state"] = "open"

        # import ipdb; ipdb.set_trace()
        issues =  _get_github_handler_lazily().search_issues(query, **qualifiers)
        return issues


    @classmethod
    def _get_queryset(cls, objects, **qualifiers):
        pass


    def __repr__(self):
        return "Issue"



class FilterOperation():
    # NOTE: only support equal operation
    @classmethod
    def filter(cls, objects, **kwargs):
        # if not isinstance(objects, list):
        #     objects = [objects]
        pass



# TODO: cache instance should use `userId:sessionId:object_name` as key
# or use nested dict
_git_object_cache = dict()

def get_base_class(name):
    if name.endswith("issue"):
        return Issue
    elif name.endswith("repository"):
        return Repository
    else:
        raise exceptions.GitHubObjectNotFoundException(name)


def get_git_object(name):
    name = name.lower()
    try:
        return _git_object_cache[name]
    except KeyError:
        base_class = get_base_class(name)
        _git_object_cache[name] = base_class
        LOG.debug("base class is %s." % base_class)
        LOG.debug("cached git objects %s." % _git_object_cache)
        return _git_object_cache[name]
