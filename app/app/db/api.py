from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from app import application
from app import exceptions
from app import log as logging
from app import models

LOG = logging.getLogger(__name__)


_ENGINE_FACADE = None


class EngineFacade(object):

    def __init__(self, sql_connection, autocommit=True,
                 expire_on_commit=False, **kwargs):
        connection_dict = sqlalchemy.engine.url.make_url(sql_connection)
        engine_args = dict()

        if 'sqlite' in connection_dict.drivername:
            engine_args["poolclass"] = StaticPool
            engine_args["connect_args"] = {"check_same_thread": False}
        else:
            engine_args["pool_size"] = application.config.get("DATABASE_MAX_POOL_SIZE", 20)
        engine_args.update(kwargs)
        self._engine = create_engine(sql_connection,
                                     pool_recycle=application.config.get("DATABASE_POOL_RECYCLE", 3600), **engine_args)

        self._session_maker = sessionmaker(bind=self._engine,
                                           autocommit=autocommit,
                                           expire_on_commit=expire_on_commit)

    def get_engine(self):
        return self._engine

    def get_session(self):
        return self._session_maker()


def _create_facade_lazily():
    global _ENGINE_FACADE

    if _ENGINE_FACADE is None:
        sql_connection = application.config.get("DATABASE_CONNECTION", "sqlite://")
        _ENGINE_FACADE = EngineFacade(sql_connection)
    return _ENGINE_FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session():
    facade = _create_facade_lazily()
    return facade.get_session()


def model_query(model, session=None):
    session = session or get_session()
    return session.query(model)


def model_get(model_class, exc_class, obj_id, session=None):
    obj = model_query(model_class, session).filter_by(id=obj_id).first()

    if not obj:
        raise exc_class(id=obj_id)
    return obj


def model_get_all(model_class, session=None):
    objs = model_query(model_class, session=session).all()
    return objs


def model_create(model_class, values):
    obj = model_class()
    obj.update(values)
    obj.save()
    return obj


def model_update(model_class, exc_class, obj_id, values, session=None):
    obj = model_get(model_class, exc_class, obj_id, session)
    values['updated_at'] = datetime.utcnow()
    obj.update(values)
    obj.save(session)
    return obj


def model_delete(model_class, obj_id):
    session = get_session()
    with session.begin():
        session.query(model_class).filter_by(id=obj_id).delete()


def user_get(obj_id):
    return model_get(models.User, exceptions.UserNotFound,
                     obj_id)


def user_get_all():
    return model_get_all(models.User)


def user_create(values):
    return model_create(models.User, values)


def user_update(obj_id, values):
    return model_update(models.User, exceptions.UserNotFound, obj_id, values)


def user_delete(obj_id):
    return model_delete(models.User, obj_id)


def user_get_by__github_login(github_login, session=None):
    user = model_query(models.User, session).\
        filter_by(github_login=github_login).first()

    if not user:
        raise exceptions.UserNotFoundByGithubLogin(github_login=github_login)
    return user


def user_get_by__slack_user_id(slack_user_id, session=None):
    user = model_query(models.User, session).\
        filter_by(slack_user_id=slack_user_id).first()

    if not user:
        raise exceptions.UserNotFoundBySlackUserId(slack_user_id=slack_user_id)
    return user


def user_get_by__token(token, session=None):
    user = model_query(models.User, session).\
        filter_by(token=token).first()

    if not user:
        raise exceptions.UserNotFoundByToken(token=token)
    return user


def user_get_by__state(state, session=None):
    user = model_query(models.User, session).\
        filter_by(state=state).first()

    if not user:
        raise
    return user
