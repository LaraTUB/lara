import json
import datetime
from github import Github
from github.GithubException import UnknownObjectException

from app import application
from app import exceptions
from app import log as logging
from app import trigger
from app import utils
from app.cache import get_cache_handler
from app.utils import serializer_fields, filter_fields, get_desired_parameters
from app.db import api as dbapi
from app.tests import fakes


LOG = logging.getLogger(__name__)


def _get_github_handler_lazily(github_login=None):
    if application.config.get("GITHUB_USERNAME") and application.config.get("GITHUB_PASSWORD"):
        LOG.debug("Get github handler via username and password")
        return Github(application.config['GITHUB_USERNAME'],
                      application.config['GITHUB_PASSWORD'])
    elif github_login:
        user = dbapi.user_get_by__github_login(github_login)
        return Github(user.github_token)
    else:
        raise exceptions.LaraException("You must provide either username&password or github token.")



def _get_organization_lazily(github_login=None):
    # TODO: organization name should be provided by the incoming request
    ORGANIZATION = _get_github_handler_lazily(github_login).\
                get_organization(application.config.get('ORGANIZATION', 'LaraTUB'))

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


    @classmethod
    def get_milestone(cls, github_login):
        if not application.config.get("OFFLINE", False):
            repo = _get_organization_lazily(github_login).get_repo("test")
            milestones = repo.get_milestones()
        else:
            milestone = fakes.FakeMileStone("fake test2", 5,
                                            datetime.datetime.utcnow(),
                                            "open")
            milestones = [milestone]

        for milestone in milestones:
            if not milestone.due_on:
                continue
            if datetime.datetime.utcnow() > milestone.due_on:
                continue

            user = dbapi.user_get_by__github_login(github_login)
            try:
                # TODO: add another table to make data model more flexiable
                dbapi.milestone_get_by(user_id=user.id, number=milestone.number)
                LOG.debug("Milestone has already cached in database.")
                continue
            except:
                pass

            values = dict(
                number=milestone.number,
                title=milestone.title,
                state=milestone.state,
                due_on=milestone.due_on,
                user_id=user.id,
                user=user,
                raw_data=json.dumps(milestone.raw_data)
            )
            dbapi.milestone_create(values)
        else:
            LOG.info("Not Found any *milestone* in repositories.")

    def __repr__(self):
        return "Repository"


class Issue():
    repository = None
    last_repository_name = None
    # TODO: place this comment content in buffer pool,
    # for example, use `sessionId`, `user-identifier` or `token`
    # to track different users
    body = ""
    _new_comment_cache = get_cache_handler()
    _new_issue_cache = get_cache_handler()
    _list_issue_cache = get_cache_handler()

    _search_fields = ("in", "author", "assignee", "mentions",
                      "involves", "team", "state", "labels",
                      "language", "is", "merged", "closed",
                      "status", "comments",
                      "project")
    @classmethod
    def _get_repository(cls, **kwargs):
        if cls.repository is not None and \
           not kwargs.get("repository", None):
            return cls.repository

        name = kwargs.pop("repository", None)

        if not name:
            raise exceptions.RepositoryNotProvidedException()


        github_login = kwargs.pop("assignee.login", None)
        # TODO: handle case-sensitive, assuming all the input repository name is lower-case.
        # Here, sanity using the newly provided repository name, although
        # the repository maybe doesn't change
        cls.repository = _get_organization_lazily(github_login).get_repo(name)
        cls.last_repository_name = name
        return cls.repository


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @filter_fields("id", "assignee.login")
    @get_desired_parameters("id", "repository", "state", "since", "labels",
                            "session_id", "assignee.login")
    def list(cls, **kwargs):
        session_id = kwargs.pop("session_id")
        if not session_id:
            raise exceptions.ServerExceptions()

        cached_kwargs = cls._list_issue_cache.get(session_id) or dict()
        id = kwargs.pop("id", None)
        state = kwargs.pop("state", "open")
        since = kwargs.pop("since", None)

        if state:
            kwargs['state'] = state
        if since:
            kwargs['since'] = utils.make_datetime(since.split("/")[0])

        cached_kwargs.update(kwargs)
        kwargs = cached_kwargs
        cls._list_issue_cache.set(session_id, kwargs)

        cls._get_repository(**kwargs)
        kwargs.pop("repository", "")
        kwargs.pop("assignee.login", "")
        if not id:
            labels = kwargs.pop("labels", None)
            issues = cls.repository.get_issues(**kwargs)
            if labels:
                issues = [issue for issue in issues for label in issue.labels if label.name in labels]
            cls._list_issue_cache.delete(session_id)
            return issues

        try:
            issues = cls.repository.get_issue(id)
            cls._list_issue_cache.delete(session_id)
            return issues

        except UnknownObjectException:
            raise exceptions.IssueIdNotFoundException(id)

    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("id", "repository", "assignee.login")
    def close(cls, **kwargs):
        cls._get_repository(**kwargs)
        kwargs.pop("repository", "")
        id = kwargs.pop("id", None)
        if not id:
            raise exceptions.IssueIdNotProvidedException()

        try:
            issue = cls.repository.get_issue(id)
        except UnknownObjectException:
            raise exceptions.IssueIdNotFoundException(id)

        issue.edit(state="closed")
        return issue


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("id", "repository", "assignee.login")
    def open(cls, **kwargs):
        cls._get_repository(**kwargs)
        kwargs.pop("repository", "")
        id = kwargs.pop("id", None)
        if not id:
            raise exceptions.IssueIdNotProvidedException()
        try:
            issue = cls.repository.get_issue(id)
        except UnknownObjectException:
            raise exceptions.IssueIdNotFoundException(id)

        issue.edit(state="open")
        return issue


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("repository", "title", "body",
                            "assignee", "labels",
                            "session_id", "assignee.login")
    def create(cls, **kwargs):
        cached_kwargs = cls._new_issue_cache.get(kwargs.get("session_id")) or dict()

        if not kwargs.get("title") and not cached_kwargs.get("title"):
            raise exceptions.IssueTitleNotProvidedException()
        if not kwargs.get("body") and not cached_kwargs.get("body"):
            raise exceptions.IssueBodyNotProvidedException()
        if not kwargs.get("assignee") and not cached_kwargs.get("assignee"):
            raise exceptions.IssueAssigneeNotProvidedException()
        if not kwargs.get("labels") and not cached_kwargs.get("labels"):
            raise exceptions.IssueLabelNotProvidedException()

        cached_kwargs.update(kwargs)
        kwargs = cached_kwargs
        cls._new_issue_cache.set(kwargs.get("session_id"), kwargs)
        kwargs.pop("session_id")

        cls._get_repository(**kwargs)
        kwargs.pop("repository", "")

        issue = cls.repository.create_issue(**kwargs)

        cls._new_issue_cache.delete(kwargs.get("session_id"))
        return issue


    @classmethod
    @serializer_fields("id", "state", "number", "title",
                       "body", "comments", "user.login",
                       "labels.name")
    @get_desired_parameters("id", "repository", "body", "finished", "session_id",
                            "assignee.login")
    def comment(cls, **kwargs):
        cls._get_repository(**kwargs)
        try:
            id = kwargs["id"]
        except KeyError:
            raise exceptions.IssueIdNotProvidedException()

        # TODO: handle incoming requests contains comment body
        body = kwargs.pop("body", "")
        session_id = kwargs.pop("session_id")

        if not session_id:
            raise exceptions.ServerException("Bad parameters received from *dialogflow*")
        cached_body = cls._new_comment_cache.get(session_id)
        _body = cached_body + "\n" + body if cached_body else body
        cls._new_comment_cache.set(session_id, _body, trigger.issue_comment_timeout_event)

        LOG.debug("Inside cache, the comment is: %s." % cls._new_comment_cache.get(session_id))
        if not kwargs.get("finished") or kwargs["finished"].upper() != "YES":
            raise exceptions.IssueCommentNotFinishedException(id)


        if not _body:
            # NOTE: keep salient
            LOG.debug("Doesn't receive any comments.")
            return

        try:
            issue = cls.repository.get_issue(id)
        except UnknownObjectException:
            raise exceptions.IssueIdNotFoundException(id)

        # TODO: check whether the issue is open?
        issue_comment = issue.create_comment(body=_body)
        # NOTE: this value is comsumed, remove it from cache
        cls._new_comment_cache.delete(session_id)

        return issue_comment


    @classmethod
    def score_pull_request(cls, name):
        cls._get_repository(repository="test")
        issues = [issue for issue in cls.repository.get_issues()]
        # print("this is {}".format(name))
        print(issues)

    @classmethod
    def _get_queryset(cls, objects, **qualifiers):
        pass

    def __repr__(self):
        return "Issue"


_git_object_cache = get_cache_handler()

def invalid_cache_object(name):
    LOG.debug("call invalid_cache_object to delete key %s" % name)
    _git_object_cache.delete(name)


def get_base_class(name):
    # NOTE: generate sub-class `github login name` and `object entity`
    if ":" in name:
        github_login, obj_name = name.split(":")
    else:
        github_login, obj_name = "GithubLogin", name

    base = None
    if name.endswith("issue"):
        base = Issue
    elif name.endswith("repository"):
        base = Repository
    else:
        raise exceptions.GitHubObjectNotFoundException(name)
    base_name = base.__name__

    klass_name = "{}{}".format(github_login.title(), base_name)
    return type(klass_name, (base,), dict())


def get_git_object(name):
    name = name.lower()
    try:
        return _git_object_cache[name]
    except KeyError:
        base_class = get_base_class(name)
        _git_object_cache.set(name, base_class, invalid_cache_object,
                              name)
        LOG.debug("Base class is %s." % base_class)
        LOG.debug("Cached git objects %s." % _git_object_cache)
        return _git_object_cache[name]
