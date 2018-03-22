from app.models.base import Base, Model
from sqlalchemy import Column, Integer, String


class User(Base, Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    github_name = Column(String(255), nullable=True)
    github_login = Column(String(255), nullable=True)
    github_token = Column(String(1024), nullable=True)
    slack_user_id = Column(String(255), nullable=True)
    token = Column(String(1024), nullable=False)
    state = Column(String(32), nullable=True)
