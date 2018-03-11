import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import object_mapper
from sqlalchemy import Column, DateTime, Boolean

from app.db import api as dbapi


Base = declarative_base()


class Model(object):
    # created_at = Column(DateTime, default=lambda: datetime.datetime.utcnow())
    # updated_at = Column(DateTime, onupdate=lambda: datetime.datetime.utcnow(),
    #                     default=lambda: datetime.datetime.utcnow())
    # is_delete = Column(Boolean, default=False)

    def save(self, session=None):
        if session is None:
            session = dbapi.get_session()

        session.add(self)
        session.flush()

    def update(self, values):
        for k, v in values.items():
            setattr(self, k, v)

    def __iter__(self):
        column = dict(object_mapper(self).columns).keys()
        self._i = iter(columns)
        return self

    def next(self):
        k = self._i.next()
        v = getattr(self, k)
        return k, v

    def delete(self):
        self.is_delete = True
        self.save()
