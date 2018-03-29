from app.models.base import Base, Model
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils.types.choice import ChoiceType


class MileStone(Base, Model):
    StateTypes = [
        (u'open', u'open'),
        (u'closed', u'closed')
    ]

    __tablename__ = "milestone"

    id = Column(Integer, primary_key=True)
    # Number: This attribute is tagged by github api.
    # It seems like a primary key 'id' for the milestone.
    number = Column(Integer, nullable=True)
    title = Column(String(1024), nullable=True)
    state = Column(ChoiceType(StateTypes, impl=String()), default='open')
    due_on = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = relationship("User", backref=backref('milestone', order_by=id))
